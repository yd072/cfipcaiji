name: collect_ips

on:
  workflow_dispatch:
  schedule:
    - cron: '0 3 * * *'

jobs:
  run-and-commit:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests beautifulsoup4 ipwhois selenium

    - name: Install chromium and chromium-driver
      run: |
        sudo apt-get update
        sudo apt-get install -y chromium-browser chromium-chromedriver

    - name: Run the yx_ips script
      env:
        CHROME_BIN: /usr/bin/chromium-browser
      run: |
        echo "Running the yx_ips script..."
        python collect_ips.py
        echo "collect_ips script completed."

    - name: Check if ip.txt exists and has content
      run: |
        if [ -f "ip.txt" ]; then cat ip.txt; else echo "ip.txt not found"; fi

    - name: Commit and push changes
      run: |
        git config --global user.email "actions@github.com"
        git config --global user.name "GitHub Actions"
        git add ip.txt
        git commit -m "Update ip.txt" || echo "No changes"
        git push origin main
