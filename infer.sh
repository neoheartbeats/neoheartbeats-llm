vllm serve /home/neoheartbeats/Neoheartbeats/models/llama-3.1-8b-inst/ \
    --enable_prefix_caching \
    --gpu_memory_utilization 0.9 \
    --max_model_len 8192