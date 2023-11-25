ssh -i "../../koteach.pem" ubuntu@ec2-18-133-26-124.eu-west-2.compute.amazonaws.com << EOF
  cd data/koteach
  sudo pkill gunicorn
  git fetch
  git reset --hard origin/main
  sudo gunicorn main:app --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 --reload --daemon --log-file koteach.log --access-logfile="koteach.log"
EOF
