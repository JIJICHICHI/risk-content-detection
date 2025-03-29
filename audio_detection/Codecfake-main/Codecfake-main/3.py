from huggingface_hub import snapshot_download

# 指定下载路径（示例路径，可按需修改）
save_path = "./pretrained_models/wav2vec2-xls-r-300m"

snapshot_download(
    repo_id="facebook/wav2vec2-xls-r-300m",
    local_dir=save_path,
    local_dir_use_symlinks=False
)
