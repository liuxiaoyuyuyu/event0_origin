#!/usr/bin/env python
#author: Wenbin Zhao (modified to use HTCondor transfer_input_files)
#email: wenbinzhao237@gmail.com

from subprocess import call, check_call
import sys
import random
import time
import os
import argparse

EOS_SRC_DIR = "/eos/cms/store/group/phys_heavyions/xiaoyul/wenbin/event0"  # directory on EOS to ship
DEFAULT_TARBALL = "event0.tgz"
DEFAULT_OUTPUT_DIR = "/eos/cms/store/group/phys_heavyions/xiaoyul/wenbin/sample"
DEFAULT_OUTPUT_PREFIX = "pp_parton_cascade"

def ensure_tarball(eos_src=EOS_SRC_DIR, tarball=DEFAULT_TARBALL):
    """
    Create a tarball from the EOS source directory on the submit host.
    The submit host (AFS/lxplus) can see /eos; the worker nodes might not.
    """
    if not os.path.isdir(eos_src):
        raise RuntimeError(f"Source directory not found on submit host: {eos_src}")

    # Always recreate tarball to ensure we have the latest changes
    if os.path.exists(tarball):
        print(f"[prep] Removing existing tarball: {tarball}")
        os.remove(tarball)
    
    print(f"[prep] Creating fresh tarball from {eos_src} -> {tarball}")
    # Pack the directory so the top-level folder inside tar is 'event0'
    # -C changes to the parent dir and tars the basename
    parent = os.path.dirname(eos_src.rstrip("/"))
    base = os.path.basename(eos_src.rstrip("/"))
    check_call(["tar", "-C", parent, "-czf", tarball, base])

def submit(njobs=1, nevent=10, batch_num=0, output_dir=None, output_prefix=None, tarball_name=DEFAULT_TARBALL):
    # Make sure logs/ exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Generate a random base seed for this batch
    random_base_seed = random.randint(0, 10**6)

    # Set defaults for output directory and prefix
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    if output_prefix is None:
        output_prefix = DEFAULT_OUTPUT_PREFIX

    # Create output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    # Full output base passed to fastjet_hadron_trackTree: dir/prefix -> dir/prefix_batchN_JOBID.root
    output_path_arg = os.path.join(output_dir, output_prefix)

    # Ensure tarball exists before we submit
    ensure_tarball(tarball=tarball_name)

    jobs = '''#!/bin/bash
set -euo pipefail

hostname
date

export PYTHIA8=/afs/cern.ch/user/x/xiaoyul/pythia8310_install
export LHAPDF_DATA_PATH=/afs/cern.ch/user/x/xiaoyul/LHAPDF_Lib/share/LHAPDF
export LD_LIBRARY_PATH=$PYTHIA8/lib:/afs/cern.ch/user/x/xiaoyul/LHAPDF_Lib/lib:$LD_LIBRARY_PATH

# Get the job ID from Condor (0 to N-1)
JOB_ID=$1

pwd
echo $_CONDOR_SCRATCH_DIR

# Create Playground directory if it doesn't exist
mkdir -p Playground

# Remove existing job directory if it exists
if [ -d "Playground/job-batch{batch_num}-$JOB_ID" ]; then
    echo "Removing existing job-batch{batch_num}-$JOB_ID directory..."
    rm -rf "Playground/job-batch{batch_num}-$JOB_ID"
fi

# Prepare job work area
mkdir -p "Playground/job-batch{batch_num}-$JOB_ID"

# Unpack shipped code (tarball) into the job directory
if [ ! -f "{tarball_name}" ]; then
    echo "FATAL: missing {tarball_name} in working dir"; ls -la; exit 99
fi

tar -xzf {tarball_name} -C "Playground/job-batch{batch_num}-$JOB_ID"

cd "Playground/job-batch{batch_num}-$JOB_ID"

# If the tar contains a top-level 'event0' folder, flatten it
if [ -d event0 ]; then
    # Move contents of event0/* into current dir (ignore hidden dotfiles if none expected)
    shopt -s dotglob || true
    mv event0/* . || true
    rmdir event0 || true
    shopt -u dotglob || true
fi

# Generate the pythia parton
cd pythia_parton
./mymain06 {nevent} $(({random_base_seed} + $JOB_ID * 12345))
cd ../

# ZPC for parton cascade
cd ZPC
mkdir -p ana
ln -sf ../pythia_parton/parton_info.dat ./

# Generate job-specific seeds for ZPC
HIJING_SEED=$(({random_base_seed} + $JOB_ID * 54321))
ZPC_SEED=$(({random_base_seed} + $JOB_ID * 98765))

# Create custom input.ampt with job-specific seeds and event number
sed "s/^0[[:space:]]*![[:space:]]*ihjsed/11      ! ihjsed/" input.ampt | \\
sed "s/^53153515[[:space:]]*![[:space:]]*random seed for HIJING/$HIJING_SEED    ! random seed for HIJING/" | \\
sed "s/^8[[:space:]]*![[:space:]]*random seed for parton cascade/$ZPC_SEED      ! random seed for parton cascade/" | \\
sed "s/^10[[:space:]]*![[:space:]]*NEVNT/{nevent}            ! NEVNT/" > input_custom.ampt

# Replace the original input.ampt with our custom one
cp input_custom.ampt input.ampt
echo $HIJING_SEED | ./exec
cd ../

# fragmentation and urqmd
cd hadronization_urqmd
cd fragmentation
ln -sf ../../ZPC/ana/zpc.dat ./
./main_string_fragmentation {nevent}

cd ../urqmd_code
    # script to run urqmd
    cd osc2u
    ln -sf ../../fragmentation/hadrons_frag1.dat ./
    ./run_osc2u_safe.sh hadrons_frag1.dat 
    rm -r ../../fragmentation/hadrons_frag1.dat
    mv fort.14 ../urqmd/OSCAR.input
    cd ../urqmd
./runqmd.sh > run.log 2>&1
rm -fr OSCAR.input
rm -rf run.log
cd ..
cd ../
cd ../
echo "=== Fragmentation and UrQMD completed ==="

# jet finding of final hadrons
echo "=== Starting FastJet analysis ==="
cd fastjet_hadron
ln -sf ../hadronization_urqmd/urqmd_code/urqmd/particle_list.dat ./
ln -sf ../pythia_parton/parton_info.dat ./
ln -sf ../ZPC/ana/zpc.dat ./
ln -sf ../ZPC/ana/zpc.res ./
ln -sf ../ZPC/ana/parton-collisionsHistory.dat ./
./fastjet_hadron {nevent} $JOB_ID {batch_num} {output_path_arg}
cd ../
echo "=== FastJet analysis completed ==="

# Clean up
rm -r fastjet_hadron
rm -r hadronization_urqmd
rm -r pythia_parton
rm -r ZPC
cd ../
rm -rf job-batch{batch_num}-$JOB_ID
cd ../
'''.format(nevent=nevent, random_base_seed=random_base_seed, batch_num=batch_num, tarball_name=tarball_name, output_path_arg=output_path_arg)

    job_name = f"NSC3_batch{batch_num}.sh"
    with open(job_name, 'w') as fout:
        fout.write(jobs)
    os.chmod(job_name, 0o755)

    condor_submit = '''universe                = vanilla
executable              = {job_name}
arguments               = $(Process)
# Transfer the executable and inputs to the worker
should_transfer_files   = YES
when_to_transfer_output = ON_EXIT_OR_EVICT
# Ship the tarball containing your code/data
transfer_input_files    = {tarball_name}

# Environment (kept from your original + terminal fix)
         environment = "PYTHIA8=/afs/cern.ch/user/x/xiaoyul/pythia8310_install; LHAPDF_DATA_PATH=/afs/cern.ch/user/x/xiaoyul/LHAPDF_Lib/share/LHAPDF; LD_LIBRARY_PATH=/afs/cern.ch/user/x/xiaoyul/pythia8310_install/lib:/afs/cern.ch/user/x/xiaoyul/LHAPDF_Lib/lib:$$LD_LIBRARY_PATH; TERM=dumb"

# Logs stay on the submit host (AFS)
output                  = logs/out_batch{batch_num}_$(Process).log
error                   = logs/err_batch{batch_num}_$(Process).log
log                     = logs/condor_batch{batch_num}.log

+MaxRuntime             = 100000
request_memory          = 8192
request_disk            = 10485760 
queue {njobs}
'''.format(job_name=job_name, tarball_name=tarball_name, batch_num=batch_num, njobs=njobs)
    job_name2 = f"Submit_batch{batch_num}.sh"
    with open(job_name2, 'w') as fout:
        fout.write(condor_submit)

    print(f"Submitting batch {batch_num}: {njobs} jobs with {nevent} events each")
    print(f"Condor submit file: {job_name2}")
    print(f"Bash script: {job_name}")

    # Submit
    call(['condor_submit', job_name2])

if __name__=='__main__':
    ap = argparse.ArgumentParser(
        description="Submit HTCondor jobs with transferred tarball.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("N_jobs", type=int, help="Number of jobs to submit")
    ap.add_argument("events_per_job", type=int, help="Events per job")
    ap.add_argument("batch_number", type=int, help="Batch number for unique output names")
    ap.add_argument("--tarball", "-t", type=str, default=DEFAULT_TARBALL,
                    help="Tarball name to create and transfer (e.g. event0.tgz)")
    ap.add_argument("--output-dir", "-d", type=str, default=DEFAULT_OUTPUT_DIR,
                    help="Output directory for root files (created if missing)")
    ap.add_argument("--output-prefix", "-p", type=str, default=DEFAULT_OUTPUT_PREFIX,
                    help="Output file name prefix (files: <prefix>_batch<N>_<jobid>.root)")
    args = ap.parse_args()

    njobs = args.N_jobs
    nevent = args.events_per_job
    batch_num = args.batch_number
    tarball_name = args.tarball
    output_dir = args.output_dir
    output_prefix = args.output_prefix

    print(f"Submitting batch {batch_num}: {njobs} jobs with {nevent} events each")
    print(f"Tarball: {tarball_name}")
    print(f"Output dir: {output_dir} (created if missing)")
    print(f"Output prefix: {output_prefix}")
    submit(njobs, nevent, batch_num, output_dir=output_dir, output_prefix=output_prefix, tarball_name=tarball_name)
