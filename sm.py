from vllm import LLM, EngineArgs
import dataclasses
import shutil
import os
from pathlib import Path

MODEL = "/home/neoheartbeats/Neoheartbeats/models/llama-3.1-8b-inst/"


def state_model():
    engine_args = EngineArgs(model=MODEL)
    output_path = "./models/sm/"
    llm = LLM(**dataclasses.asdict(engine_args))
    Path(output_path).mkdir(exist_ok=True)
    model_executor = llm.llm_engine.model_executor
    model_executor.save_sharded_state(path=output_path)
    model_path = MODEL
    for file in os.listdir(model_path):
        if os.path.splitext(file)[1] not in (".bin", ".pt", ".safetensors"):
            if os.path.isdir(os.path.join(model_path, file)):
                shutil.copytree(
                    os.path.join(model_path, file), os.path.join(output_path, file)
                )
            else:
                shutil.copy(os.path.join(model_path, file), output_path)


if __name__ == "__main__":
    state_model()
