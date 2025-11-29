import torch


def get_default_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"
