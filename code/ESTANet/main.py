import torch
from torch.utils.tensorboard import SummaryWriter
import argparse
import yaml
import os
import os.path as osp
from utils import get_logger, set_seed, create_outdir
from model import build_two_model
from datasets import build_data_loader
from criterions import build_criterion
from trainer import build_trainer, build_eval

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", type=str
    )
    parser.add_argument("--eval", type=str, default=None)
    parser.add_argument("--tensorboard", action="store_true")
    parser.add_argument("--vis", action="store_true")

    args = parser.parse_args()

    args.tensorboard = True
    # combine argparse and yaml
    opt = yaml.load(open(args.config), Loader=yaml.FullLoader)
    opt.update(vars(args))
    cfg = opt

    set_seed(20)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    testloader = build_data_loader(cfg, mode="test")
    trainloader = build_data_loader(cfg, mode="train")

    model, model2 = build_two_model(cfg, device)
    evaluate = build_eval(cfg)

    if args.eval != None:
        model.load_state_dict(torch.load(os.path.join(args.eval, "ckpts/best_error.pth")))
        model2.load_state_dict(torch.load(os.path.join(args.eval, "ckpts/best_error2.pth")))
        tas_s_results, tas_l_results, tas_s_results2, tas_l_results2, mul_ed_results = evaluate.eval_tas_error(
            model,
            model2,
            testloader,
            args.eval,
            device,
            vis=args.vis
        )
        print("Temporal Action Segmentation Results:")
        print("(Small) Robust Action Detector, \tAcc:%.1f, Acc-bg:%.1f, Edit:%.1f, F1@10:%.1f, F1@25:%.1f, F1@50:%.1f" % (tas_s_results['Acc'], tas_s_results['Acc-bg'], tas_s_results['Edit'], tas_s_results['F1@10'], tas_s_results['F1@25'], tas_s_results['F1@50']))
        print("(Small) Sensitive Action Detector, \tAcc:%.1f, Acc-bg:%.1f, Edit:%.1f, F1@10:%.1f, F1@25:%.1f, F1@50:%.1f" % (tas_s_results2['Acc'], tas_s_results2['Acc-bg'], tas_s_results2['Edit'], tas_s_results2['F1@10'], tas_s_results2['F1@25'], tas_s_results2['F1@50']))
        print("============================================================================================================")
        print("(Large) Robust Action Detector, \tAcc:%.1f, Acc-bg:%.1f, Edit:%.1f, F1@10:%.1f, F1@25:%.1f, F1@50:%.1f" % (tas_l_results['Acc'], tas_l_results['Acc-bg'], tas_l_results['Edit'], tas_l_results['F1@10'], tas_l_results['F1@25'], tas_l_results['F1@50']))
        print("(Large) Sensitive Action Detector, \tAcc:%.1f, Acc-bg:%.1f, Edit:%.1f, F1@10:%.1f, F1@25:%.1f, F1@50:%.1f" % (tas_l_results2['Acc'], tas_l_results2['Acc-bg'], tas_l_results2['Edit'], tas_l_results2['F1@10'], tas_l_results2['F1@25'], tas_l_results2['F1@50']))
        print("============================================================================================================")
        
        print()
        print("Online Error Detection Results")
        if "EPIC-TENT-O" in cfg["data_name"] or "ASSEMBLY101-O" in cfg["data_name"]:
            mul_ed_results, mul_ed_n_results = mul_ed_results
            print(f"|{'Correct Precision':^{15}}|{'Mistake Precision':^{15}}|{'Avg Precision':^{15}}|")
            print(f"|{'---':^{15}}|{'---':^{15}}|{'---':^{15}}|")
            avgprecision = (mul_ed_n_results['precision'] + mul_ed_results['precision']) / 2
            print(f"|{mul_ed_results['precision']:^{15}.1f}|{mul_ed_n_results['precision']:^{15}.1f}|{avgprecision:^{15}.1f}|")
            print(f"|{'Correct Recall':^{15}}|{'Mistake Recall':^{15}}|{'Avg Recall':^{15}}|")
            print(f"|{'---':^{15}}|{'---':^{15}}|{'---':^{15}}|")
            avgrecall = (mul_ed_n_results['recall'] + mul_ed_results['recall']) / 2
            print(f"|{mul_ed_results['recall']:^{15}.1f}|{mul_ed_n_results['recall']:^{15}.1f}|{avgrecall:^{15}.1f}|")
            print(f"|{'Correct F1':^{15}}|{'Mistake F1':^{15}}|{'Avg F1':^{15}}|")
            print(f"|{'---':^{15}}|{'---':^{15}}|{'---':^{15}}|")
            avgf1 = (mul_ed_n_results['f1'] + mul_ed_results['f1']) / 2
            print(f"|{mul_ed_results['f1']:^{15}.1f}|{mul_ed_n_results['f1']:^{15}.1f}|{avgf1:^{15}.1f}|")
        else:
            print(f"|{'F1@10:':^{15}}|{'F1@25:':^{15}}|{'F1@50:':^{15}}|")
            print(f"|{'---':^{15}}|{'---':^{15}}|{'---':^{15}}|")
            print(f"|{mul_ed_results['All-F1@10']:^{15}.1f}|{mul_ed_results['All-F1@25']:^{15}.1f}|{mul_ed_results['All-F1@50']:^{15}.1f}|")
        exit()
    
    identifier = f'{cfg["task"]}_{cfg["data_name"]}'
    result_path = create_outdir(osp.join(cfg["output_path"], identifier))
    logger = get_logger(result_path)
    logger.info(cfg)

    trainloader = build_data_loader(cfg, mode="train")
    criterion = build_criterion(cfg, device)
    train_one_epoch = build_trainer(cfg)
    optim = torch.optim.AdamW if cfg["optimizer"] == "AdamW" else torch.optim.Adam
    optimizer = optim(
        [{"params": model.parameters(), "initial_lr": cfg["lr"]}],
        lr=cfg["lr"],
        weight_decay=cfg["weight_decay"],
    )
    if "lr2" not in cfg:
        cfg["lr2"] = cfg["lr"]
    optimizer2 = optim(
        [{"params": model2.parameters(), "initial_lr": cfg["lr2"]}],
        lr=cfg["lr2"],
        weight_decay=cfg["weight_decay"],
    )


    writer = SummaryWriter(osp.join(result_path, "runs")) if args.tensorboard else None
    total_params = sum(p.numel() for p in model.parameters())

    writer2 = SummaryWriter(osp.join(result_path, "runs")) if args.tensorboard else None
    total_params2 = sum(p.numel() for p in model2.parameters())

    logger.info(f'Dataset: {cfg["data_name"]},  Model: {cfg["model"]}, Model: {cfg["model2"]}')
    logger.info(
        f'lr:{cfg["lr"]} | lr2:{cfg["lr2"]} | Weight Decay:{cfg["weight_decay"]} | Batch Size:{cfg["batch_size"]}'
    )
    logger.info(
        f'Total epoch:{cfg["num_epoch"]} | Total Params:{(total_params+total_params2)/1e6:.1f} M | Optimizer: {cfg["optimizer"]}'
    )
    logger.info(f"Output Path:{result_path}")

    best_avgf1, best_epoch = 0, 0
    best_avgf1_2, best_epoch_2 = 0, 0
    best_ef1 = 0
    global_it = 0
    for epoch in range(1, cfg["num_epoch"] + 1):
        model.train()
        model2.train()

        # first model
        epoch_loss, global_it = train_one_epoch(
            trainloader,
            model,
            criterion,
            optimizer,
            epoch,
            device, 
            writer,
            model_idx=1,
            data_name=cfg["data_name"],
            global_it=global_it
        )

        trainloader.dataset._load_features(cfg)
        trainloader.dataset._init_features()

        # second model
        epoch_loss, global_it = train_one_epoch(
            trainloader,
            model2,
            criterion,
            optimizer2,
            epoch,
            device,
            writer2,
            model_idx=2,
            data_name=cfg["data_name"],
            global_it=global_it,
            std_model=model
        )

        tas_s_results, tas_l_results, tas_s_results2, tas_l_results2, mul_ed_results = evaluate.eval_tas_error(
            model,
            model2,
            testloader,  
            result_path,
            device
        )
        print("Temporal Action Segmentation Results")
        print("============================================================================================================")
        print("(Small) Robust Action Detector, \tAcc:%.1f, Acc-bg:%.1f, Edit:%.1f, F1@10:%.1f, F1@25:%.1f, F1@50:%.1f" % (tas_s_results['Acc'], tas_s_results['Acc-bg'], tas_s_results['Edit'], tas_s_results['F1@10'], tas_s_results['F1@25'], tas_s_results['F1@50']))
        print("(Small) Sensitive Action Detector, \tAcc:%.1f, Acc-bg:%.1f, Edit:%.1f, F1@10:%.1f, F1@25:%.1f, F1@50:%.1f" % (tas_s_results2['Acc'], tas_s_results2['Acc-bg'], tas_s_results2['Edit'], tas_s_results2['F1@10'], tas_s_results2['F1@25'], tas_s_results2['F1@50']))
        print("============================================================================================================")
        print("(Large) Robust Action Detector, \tAcc:%.1f, Acc-bg:%.1f, Edit:%.1f, F1@10:%.1f, F1@25:%.1f, F1@50:%.1f" % (tas_l_results['Acc'], tas_l_results['Acc-bg'], tas_l_results['Edit'], tas_l_results['F1@10'], tas_l_results['F1@25'], tas_l_results['F1@50']))
        print("(Large) Sensitive Action Detector, \tAcc:%.1f, Acc-bg:%.1f, Edit:%.1f, F1@10:%.1f, F1@25:%.1f, F1@50:%.1f" % (tas_l_results2['Acc'], tas_l_results2['Acc-bg'], tas_l_results2['Edit'], tas_l_results2['F1@10'], tas_l_results2['F1@25'], tas_l_results2['F1@50']))
        print("============================================================================================================")

        print()
        print("Online Error Detection Results")
        if "EPIC-TENT-O" in cfg["data_name"] or "ASSEMBLY101-O" in cfg["data_name"]:
            mul_ed_results, mul_ed_n_results = mul_ed_results
            print(f"|{'N F1':^{15}}|{'E F1':^{15}}|{'F1':^{15}}|")
            print(f"|{'---':^{15}}|{'---':^{15}}|{'---':^{15}}|")
            ef1 = (mul_ed_results["f1"] + mul_ed_n_results["f1"]) / 2
            print(f"|{mul_ed_n_results['f1']:^{15}.1f}|{mul_ed_results['f1']:^{15}.1f}|{ef1:^{15}.1f}|")
        else:
            print(f"|{'F1@10:':^{15}}|{'F1@25:':^{15}}|{'F1@50:':^{15}}|")
            print(f"|{'---':^{15}}|{'---':^{15}}|{'---':^{15}}|")
            print(f"|{mul_ed_results['All-F1@10']:^{15}.1f}|{mul_ed_results['All-F1@25']:^{15}.1f}|{mul_ed_results['All-F1@50']:^{15}.1f}|")
            ef1 = (mul_ed_results["All-F1@10"] + mul_ed_results["All-F1@25"] + mul_ed_results["All-F1@50"]) / 3

        if ef1 > best_ef1:
            best_ef1 = ef1
            print("Best Error Checkpoint Saved at %d" % epoch)
            torch.save(model.state_dict(), osp.join(result_path, "ckpts", "best_error.pth"))
            torch.save(model2.state_dict(), osp.join(result_path, "ckpts", "best_error2.pth"))
        print("============================================================================================================")