vllm serve /home/neoheartbeats/Neoheartbeats/models/llama-3.1-8b-inst/ \
    --served-model-name='llama-3.1-8b-inst' \
    --dtype="bfloat16" \
    --max-model-len=32768 \
    --enable-prefix-caching