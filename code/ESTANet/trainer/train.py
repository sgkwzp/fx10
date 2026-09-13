from tqdm import tqdm
import torch
from trainer.train_builder import TRAINER
import random

@TRAINER.register("ESTANet")
def train_epoch(trainloader, model, criterion, optimizer, epoch, device, writer=None, model_idx=1, data_name="EgoPER", global_it=0, std_model=None):
    epoch_loss = 0
    with tqdm(trainloader) as pbar:
        for it, (vid, rgb_input, target, start, end) in enumerate(pbar):
            s_rgb_input, l_rgb_input = rgb_input
            s_target, l_target = target
            s_rgb_input, l_rgb_input = s_rgb_input.to(device), l_rgb_input.to(device)
            s_target, l_target = s_target.to(device), l_target.to(device)
            
            model.train()
            
            out_dict = model(s_rgb_input, l_rgb_input, s_target, l_target)

            if std_model is not None:
                std_out_dict = std_model(s_rgb_input, l_rgb_input)
                loss_dict = criterion(out_dict, s_target, l_target, model_idx, std_out_dict)
            else:
                loss_dict = criterion(out_dict, s_target, l_target, model_idx)
            loss = 0
            for k, l in loss_dict.items():
                if "marg" not in k:
                    loss += l
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            
            out_dict = {}
            for k, l in loss_dict.items(): 
                out_dict[k] = l.item()
            pbar.set_postfix(out_dict)
            pbar.set_description(f"Epoch {epoch}, Iteration {it+(epoch-1)*len(trainloader)}")
            
            epoch_loss += loss.item()
            if writer != None:
                for k, l in loss_dict.items(): 
                    # writer.add_scalar("%s" % k, l.item(), it+epoch*len(trainloader))
                    writer.add_scalar("%s" % k, l.item(), global_it)
                global_it += 1

            if "EPIC-TENT-O" in data_name:
                if it > len(pbar) // 25:
                    print("Early Stop....................")
                    break
            elif "ASSEMBLY101-O" in data_name:
                if it > len(pbar) // 30:
                    print("Early Stop....................")
                    break

    return epoch_loss, global_it