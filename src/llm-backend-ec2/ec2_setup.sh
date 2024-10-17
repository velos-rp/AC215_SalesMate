sudo apt-get update
sudo apt install python3-pip
sudo apt install screen

pip3 install git+https://github.com/huggingface/transformers.git  --break-system-packages
pip3 install accelerate --break-system-packages
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu  --break-system-packages
pip3 install flask --break-system-packages