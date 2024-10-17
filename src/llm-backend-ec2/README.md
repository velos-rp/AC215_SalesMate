### EC2 Instance Setup

1. Navigate to EC2 Dashboard in AWS console
2. Select "Launch Instance"
3. Settings:
  a. Name: LLM API (or similar)
  b. Amazon Machine Image: Ubuntu -> Ubuntu Server 24.04 LTS (HVM), SSD Volume Type
  c. Instance Type: c5.large
  d. Key pair name: Create key pair -> RSA, .pem
  e. Network Settings: Click Edit
    i. Rule 1 -> Make sure "Source Type" is "Anywhere"
    ii. Add security group rule
      * Type: "Custom TCP"
      * Port Range: 5000
      * Source Type: "Anywhere"
      * Description: Flask API
  f. Configure Storage: 1x 30GiB gp3
4. Click Launch Instance to confirm
5. Navigate to Instances
6. Once instance is running and passed status checks, right click -> "Connect"
7. Upload `tinyllama_api.py` and `ec2_setup.sh` either through ssh or copying and pasting via `vi` or `nano`
8. Run `bash ec2_setup.sh`
9. Run `screen -S tinyllama`
10. This will create a background process "screen". Within it, run `python3 tinyllama_api.py`
11. To detach from the screen, `Ctrl + A, then D`
12. To reattach the screen, run `screen -r tinyllama`
13. To stop the process, `Ctrl + C` within the screen
14. Exit the screen using `screen -XS tinyllama quit`