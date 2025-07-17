#!/bin/bash

# Place and route binaries
KICAD_PARSER=${RL_PCB}/bin/kicadParser
SA_PCB=${RL_PCB}/bin/sa
PCB_ROUTER=${RL_PCB}/bin/pcb_router

EXP_DIR=${PWD}
export EXP_DIR=${EXP_DIR}
echo "Script launched from ${EXP_DIR}"
echo "RL_PCB repository root is ${RL_PCB}"

mkdir -p work
echo "Starting tensorboard ... "
tensorboard --logdir ./work/ --host 0.0.0.0 --port 6003 &
sleep 2

cd ${RL_PCB}/src/training

./scheduler.sh --run_config ${EXP_DIR}/run_config_a.txt --logfile $EXP_DIR/scheduler_a.log --instances 6 --yes 
./scheduler.sh --run_config ${EXP_DIR}/run_config_b.txt --logfile $EXP_DIR/scheduler_b.log --instances 6 --yes 

cd ${EXP_DIR}

python report_config.py 

cd ${RL_PCB}/src/report_generation
python generate_experiment_report.py --dir ${EXP_DIR}/work --hyperparameters ${EXP_DIR}/hyperparameters/hp_td3.json ${EXP_DIR}/hyperparameters/hp_sac.json --report_config ${EXP_DIR}/report_config.json --output ${EXP_DIR}/experiment_report.pdf -y --tmp_dir ${EXP_DIR}/tmp
cd ${EXP_DIR}

# Check if all place and route binaries exist
if [ -e "$KICAD_PARSER" ] && [ -e "$SA_PCB" ] && [ -e "$PCB_ROUTER" ]; then
    echo "Starting evaluation ..."
    cd ${RL_PCB}/src/evaluation_scripts
    TD3_EVAL_TESTING_DIR=${EXP_DIR}/work/eval_testing_set
    SAC_EVAL_TESTING_DIR=${EXP_DIR}/work/eval_testing_set

    #./eval_just_do_it.sh -p ${RL_PCB}/dataset/base/evaluation.pcb -b ${RL_PCB}/dataset/base_raw --bin_dir ${RL_PCB}/bin --path_prefix "" -d ${EXP_DIR}/work -e ablation_experiment_055,ablation_experiment_028,ablation_experiment_082 --report_type both,mean -o ${TD3_EVAL_TESTING_DIR} --runs 2 --max_steps 200 --report_type both,mean --skip_simulated_annealing 
    ./eval_just_do_it.sh -p ${RL_PCB}/dataset/base_opt/evaluation.pcb -b ${RL_PCB}/dataset/base_raw --bin_dir ${RL_PCB}/bin --path_prefix "" -d ${EXP_DIR}/work -e ablation_expert_experiment_055,ablation_expert_experiment_028,ablation_expert_experiment_082,ablation_expert_experiment_505,ablation_expert_experiment_802,ablation_expert_experiment_208 --report_type both,mean -o ${TD3_EVAL_TESTING_DIR} --runs 4 --max_steps 600 --device cpu

    cd ${EXP_DIR}
else
    echo "One or more place and route binaries expected at ${RL_PCB}/bin were not found."
fi