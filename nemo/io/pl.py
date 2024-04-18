import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, Union

<<<<<<< HEAD
import pytorch_lightning as pl
import torch
from lightning_fabric.plugins.io.checkpoint_io import CheckpointIO
from lightning_fabric.utilities.cloud_io import get_filesystem
from lightning_fabric.utilities.types import _PATH
=======
import lightning as L
import torch
from lightning.fabric.plugins.io.checkpoint_io import CheckpointIO
from lightning.fabric.utilities.cloud_io import get_filesystem
from lightning.fabric.utilities.types import _PATH
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)
from torch import nn
from typing_extensions import override


log = logging.getLogger(__name__)


<<<<<<< HEAD
LightningModuleT = TypeVar("LightningModuleT", bound=pl.LightningModule)
=======
LightningModuleT = TypeVar("LightningModuleT", bound=L.LightningModule)
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)
ModuleT = TypeVar("ModuleT", bound=nn.Module)


class MegatronCheckpointIO(CheckpointIO):
    """CheckpointIO that utilizes :func:`torch.save` and :func:`torch.load` to save and load checkpoints respectively,
    common for most use cases.

    .. warning::  This is an :ref:`experimental <versioning:Experimental API>` feature.

    """

    @override
    def save_checkpoint(self, checkpoint: Dict[str, Any], path: _PATH, storage_options: Optional[Any] = None) -> None:
        """Save model/training states as a checkpoint file through state-dump and file-write.

        Args:
            checkpoint: dict containing model and trainer state
            path: write-target path
            storage_options: not used in ``TorchCheckpointIO.save_checkpoint``

        Raises
        ------
            TypeError:
                If ``storage_options`` arg is passed in

        """
        from megatron.core import dist_checkpointing
<<<<<<< HEAD

=======
        
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)
        if storage_options is not None:
            raise TypeError(
                "`Trainer.save_checkpoint(..., storage_options=...)` with `storage_options` arg"
                f" is not supported for `{self.__class__.__name__}`. Please implement your custom `CheckpointIO`"
                " to define how you'd like to use `storage_options`."
            )
        checkpoint_dir = ckpt_to_dir(path)
        fs = get_filesystem(checkpoint_dir)
        if fs.isdir(checkpoint_dir) and dist_checkpointing.check_is_distributed_checkpoint(checkpoint_dir):
            logging.info(f'Distributed checkpoint at path {checkpoint_dir} already exists, skipping saving')
            return
<<<<<<< HEAD

=======
        
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)
        fs.makedirs(checkpoint_dir, exist_ok=True)
        dist_checkpointing.save(sharded_state_dict=checkpoint, checkpoint_dir=str(checkpoint_dir))

    @override
    def load_checkpoint(
<<<<<<< HEAD
        self, path: _PATH, sharded_state_dict=None, map_location: Optional[Callable] = None
=======
        self, 
        path: _PATH,
        sharded_state_dict=None,
        map_location: Optional[Callable] = None
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)
    ) -> Dict[str, Any]:
        """Loads checkpoint using :func:`torch.load`, with additional handling for ``fsspec`` remote loading of files.

        Args:
            path: Path to checkpoint
            map_location: a function, :class:`torch.device`, string or a dict specifying how to remap storage
                locations.

        Returns: The loaded checkpoint.

        Raises
        ------
            FileNotFoundError: If ``path`` is not found by the ``fsspec`` filesystem

        """
        from megatron.core import dist_checkpointing
<<<<<<< HEAD

        if map_location is not None:
            raise ValueError("`map_location` argument is not supported for `MegatronCheckpointIO.load_checkpoint`.")
=======
        
        if map_location is not None:
            raise ValueError(
                "`map_location` argument is not supported for `MegatronCheckpointIO.load_checkpoint`."
            )
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)

        # Try to read the checkpoint at `path`. If not exist, do not restore checkpoint.
        fs = get_filesystem(path)
        if not fs.exists(path):
            raise FileNotFoundError(f"Checkpoint file not found: {path}")
        if not fs.isdir(path):
<<<<<<< HEAD
            raise ValueError(f"Distributed checkpoints should be a directory. Found: {path}.")

        # return pl_load(path, map_location=map_location)

        checkpoint = dist_checkpointing.load(sharded_state_dict=sharded_state_dict, checkpoint_dir=str(path))
=======
            raise ValueError(
                f"Distributed checkpoints should be a directory. Found: {path}."
            )
            
        # return pl_load(path, map_location=map_location)

        checkpoint = dist_checkpointing.load(
            sharded_state_dict=sharded_state_dict, checkpoint_dir=str(path)
        )
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)
        checkpoint = _fix_tensors_device(checkpoint)

        return checkpoint

    @override
    def remove_checkpoint(self, path: _PATH) -> None:
        """Remove checkpoint file from the filesystem.

        Args:
            path: Path to checkpoint

        """
        fs = get_filesystem(path)
        if fs.exists(path):
            fs.rm(path, recursive=True)
            log.debug(f"Removed checkpoint: {path}")


def _fix_tensors_device(ckpt: Dict) -> Dict:
    """Ensure checkpoint tensors are on the correct device."""
    assert torch.cuda.is_initialized(), (torch.cuda.is_available(), torch.cuda.is_initialized())
    cur_dev = torch.device("cuda", index=torch.cuda.current_device())
<<<<<<< HEAD

=======
    
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)
    from megatron.core.dist_checkpointing.dict_utils import dict_list_map_outplace

    def _fix_device(t):
        if isinstance(t, torch.Tensor) and t.is_cuda and t.device != cur_dev:
            t = t.to(cur_dev)
        return t

    return dict_list_map_outplace(_fix_device, ckpt)


def ckpt_to_dir(filepath: Union[str, Path]) -> Path:
    """PTL considers checkpoints as .ckpt files.
    This method removes the extension and returns a path
    to be used as a directory for distributed checkpoints.
    """
    filepath = Path(filepath)
<<<<<<< HEAD

=======
    
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)
    if not filepath.suffix == ".ckpt":
        filepath = filepath.with_suffix(filepath.suffix + ".ckpt")

    # adding this assert because we will later remove directories based on the return value of this method
    assert filepath.suffix == ".ckpt", f"filepath: {filepath} must have .ckpt extension"

    # create a new path whose name is the original filepath without the .ckpt extension
    checkpoint_dir = filepath.with_name(filepath.stem)

    return checkpoint_dir


def is_distributed_ckpt(path) -> bool:
    """Check if the given path corresponds to a distributed checkpoint directory.

    This function determines if the specified path is a directory that contains a distributed
    checkpoint by checking the directory's metadata.

    Args:
        path (Union[str, Path]): The path to check for being a distributed checkpoint.

    Returns
    -------
        bool: True if the path is a distributed checkpoint directory, False otherwise.

    """
    from megatron.core import dist_checkpointing
<<<<<<< HEAD

=======
        
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)
    checkpoint_dir = ckpt_to_dir(path)
    fs = get_filesystem(checkpoint_dir)
    if fs.isdir(checkpoint_dir) and dist_checkpointing.check_is_distributed_checkpoint(checkpoint_dir):
        return True
<<<<<<< HEAD

=======
    
>>>>>>> f8ef68139 (Move over _strategy_liMegatronCheckpointIO)
    return False
