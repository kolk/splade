import hydra
from omegaconf import DictConfig

from conf.CONFIG_CHOICE import CONFIG_NAME, CONFIG_PATH
from .datasets.dataloaders import CollectionDataLoader
from .datasets.datasets import CollectionDatasetPreLoad
from .models.models_utils import get_model
from .tasks.transformer_evaluator import SparseIndexing
from .utils.utils import get_initialize_config
from omegaconf import OmegaConf,open_dict


@hydra.main(config_path=CONFIG_PATH, config_name=CONFIG_NAME)
def index(exp_dict: DictConfig):
    exp_dict, config, init_dict, model_training_config = get_initialize_config(exp_dict)

    model = get_model(config, init_dict)

    d_collection = CollectionDatasetPreLoad(data_dir=exp_dict["data"]["COLLECTION_PATH"], id_style="row_id")
    d_loader = CollectionDataLoader(dataset=d_collection, tokenizer_type=model_training_config["tokenizer_type"],
                                    max_length=model_training_config["max_length"],
                                    batch_size=config["index_retrieve_batch_size"],
                                    shuffle=False, num_workers=10, prefetch_factor=4)
    ## TO-DO: Modify Config for adapter_name
    if "adapter_name" in init_dict.keys():
        OmegaConf.set_struct(config, True)
        with open_dict(config):
            config.adapter_name = init_dict["adapter_name"]
        OmegaConf.set_struct(config, False)
    evaluator = SparseIndexing(model=model, config=config, compute_stats=True)
    evaluator.index(d_loader)


if __name__ == "__main__":
    index()
