__all__ = ['build_model']

from utils import Registry

META_ARCHITECTURES = Registry()

def build_model(cfg, device=None):
    model = META_ARCHITECTURES[cfg["model"]](cfg)
    return model.to(device)

def build_two_model(cfg, device=None):
    model = META_ARCHITECTURES[cfg["model"]](cfg, device)
    model2 = META_ARCHITECTURES[cfg["model2"]](cfg, device)
    return model.to(device), model2.to(device)