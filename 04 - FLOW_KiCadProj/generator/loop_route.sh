# Freerouting is not deterministic: retry until the DRC has no unconnected items (max 5 runs)
cd /home/claude/genFlow
for i in 1 2 3 4 5; do
  bash route_all.sh > /tmp/claude-0/flow_route.log 2>&1
  if ! grep -q "unconnected_items" /tmp/claude-0/flow_route.log; then echo "clean after run $i"; tail -8 /tmp/claude-0/flow_route.log; exit 0; fi
  echo "run $i:"; grep "unconnected_items :" /tmp/claude-0/flow_route.log
done
