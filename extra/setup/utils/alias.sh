
cat > ~/.bash_aliases << 'EOF'
#####################################################################
### Show logs docker container
#####################################################################
alias dlog='function _dlog(){ docker logs $1; };_dlog'
alias denter='function _denter(){ docker exec -it $1 sh; };_denter'
alias dstop='function _dstop(){ docker stop $1 ; };_dstop'
alias dstart='function _dstart(){ docker start $1 ; };_dstart'
alias drestart='function _drestart(){ docker restart $1; };_drestart'
alias dcreload='function _dcreload(){ docker-compose down && docker-compose up -d; };_dcreload'




# Get latest container ID
alias dl="docker ps -l -q"
# Get container process
alias dps="docker ps"
# Get process included stop container
alias dpa="docker ps -a"
# Get images
alias di="docker images"
# Get container IP
alias dip="docker inspect --format '{{ .NetworkSettings.IPAddress }}'"

function dclean(){
FILE=$(docker inspect $1 | grep -G '"LogPath": "*"' | sed -e 's/.*"LogPath": "//g' | sed -e 's/",//g') 
sudo sh -c "echo ' ' > $FILE"
}

EOF
source ~/.bash_aliases 

