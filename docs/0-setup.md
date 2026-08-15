# install node

## WSL2 패키지 목록 업데이트 및 필수 도구 설치

```zsh
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git build-essential
```

## nvm 설치

```zsh
# 설치 스크립트 다운로드 및 실행
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
# 터미널 환경변수 등 설정
source ~/.zshrc
# 설치 완료 확인 (버전)
nvm --version
```

## Node 설치

```zsh
# 최신 LTS 버전 설치
nvm install --lts
# Node, NPM 버전 확인
node -v
npm -v
```

# Frontend App 설정

```zsh
cd apps
npm create vue@latest frontend
cd frontend
npm install
npm run format
npm run dev
```

   git init && git add -A && git commit -m "initial commit"