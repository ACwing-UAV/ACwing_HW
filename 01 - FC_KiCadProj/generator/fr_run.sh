# usage: fr_run.sh in.dsn out.ses workdir passes
mkdir -p "$3"; cd "$3"; nohup java -Xmx4g -Djava.io.tmpdir="$3" -jar /home/claude/tools/fr.jar -de "$1" -do "$2" --router.max_passes=$4 --router.max_threads=4 --gui.enabled=false > "$3/run.log" 2>&1 &
echo started
