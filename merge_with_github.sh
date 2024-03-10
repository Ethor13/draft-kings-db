git add .
git commit -m "add files"
git pull
git checkout --ours -- .
git add .
git commit -m "merge"
git push