# Demo os.killpg

Often some Python code will need to spawn a subprocess.

Sometimes the code will wait for the subprocess to finish,
other times it will need to kill it before it finishes,
e.g. when the user hits Ctrl+C.

In either case,
the subprocess could have spawned subprocesses of its own
(each of which could have spawned subprocesses of its own...),
and the Python code should make sure that
(not just the immediate child process but)
all descendent processes
have stopped running, so as to clean up properly.
(If the descendents are all e.g. inheriting
the Python process's stdout/stderr
so that their output can be displayed to the user,
failing to clean up all descendent processes
means they can continue to write to the console,
even after the Python process itself has finished running.
This is fairly common when a subprocess is a shell script,
especially if it pipes one command into another.

It's difficult to solve this problem in general
since operating systems don't provide good APIs
to guarantee [structured concurrency](https://en.wikipedia.org/wiki/Structured_concurrency)
across subprocesses.

But it is easy to fix this in the following common case:
* you're running on a Unix
* you control the descendent processes that are spawned
  and can make sure they don't misbehave
  (e.g. start a new [process group](https://en.wikipedia.org/wiki/Process_group))

Better still, this is fixable entirely with the Python standard library.
No need to bring in psutil or any other 3rd-party packages.

See the code in this repo for an example.

See https://biriukov.dev/docs/fd-pipe-session-terminal/3-process-groups-jobs-and-sessions/
for more information.

```
❯ ./parent.py
[14:52:58 cmd='./parent.py'          pid=106497  pgid=106497  ppid=1652153] Running...
[14:52:58 cmd='./parent.py'          pid=106497  pgid=106497  ppid=1652153] Spawning subprocess in new process group...
[14:52:58 cmd='./parent.py'          pid=106497  pgid=106497  ppid=1652153] Sleeping 5s...
[14:52:58 cmd='./child.py --depth=0' pid=106498  pgid=106498  ppid=106497 ]   😈 Running in simulate_hang mode: will ignore SIGTERM
[14:52:58 cmd='./child.py --depth=0' pid=106498  pgid=106498  ppid=106497 ]   😈 Spawning './child.py --depth=1'
[14:52:58 cmd='./child.py --depth=0' pid=106498  pgid=106498  ppid=106497 ]   😈 Sleeping for 3s...
[14:52:58 cmd='./child.py --depth=1' pid=106499  pgid=106498  ppid=106498 ]      Running...
[14:52:58 cmd='./child.py --depth=1' pid=106499  pgid=106498  ppid=106498 ]      Spawning './child.py --depth=2'
[14:52:58 cmd='./child.py --depth=1' pid=106499  pgid=106498  ppid=106498 ]      Exiting now -> my descendants will outlive me
[14:52:58 cmd='./child.py --depth=2' pid=106500  pgid=106498  ppid=1      ]        Running...
[14:52:58 cmd='./child.py --depth=2' pid=106500  pgid=106498  ppid=1      ]        Spawning './child.py --depth=3'
[14:52:58 cmd='./child.py --depth=2' pid=106500  pgid=106498  ppid=1      ]        Sleeping for 3s...
[14:52:58 cmd='./child.py --depth=3' pid=106501  pgid=106498  ppid=106500 ]          Running...
[14:52:58 cmd='./child.py --depth=3' pid=106501  pgid=106498  ppid=106500 ]          Sleeping for 3s...
[14:53:01 cmd='./child.py --depth=0' pid=106498  pgid=106498  ppid=106497 ]   😈 Sleeping for 3s...
[14:53:01 cmd='./child.py --depth=2' pid=106500  pgid=106498  ppid=1      ]        Sleeping for 3s...
[14:53:01 cmd='./child.py --depth=3' pid=106501  pgid=106498  ppid=106500 ]          Sleeping for 3s...
[14:53:03 cmd='./parent.py'          pid=106497  pgid=106497  ppid=1652153] Woke up
[14:53:03 cmd='./parent.py'          pid=106497  pgid=106497  ppid=1652153] Sent SIGTERM to process group 106498
[14:53:03 cmd='./parent.py'          pid=106497  pgid=106497  ppid=1652153] Sleeping 3s to give subprocesses a chance to exit gracefully
[14:53:03 cmd='./child.py --depth=0' pid=106498  pgid=106498  ppid=106497 ]   😈 Received SIGTERM -> ignoring!
[14:53:03 cmd='./child.py --depth=2' pid=106500  pgid=106498  ppid=1      ]        Received SIGTERM -> exiting
[14:53:03 cmd='./child.py --depth=3' pid=106501  pgid=106498  ppid=106500 ]          Received SIGTERM -> exiting
[14:53:04 cmd='./child.py --depth=0' pid=106498  pgid=106498  ppid=106497 ]   😈 Sleeping for 3s...
[14:53:06 cmd='./parent.py'          pid=106497  pgid=106497  ppid=1652153] Sent SIGKILL to process group 106498
[14:53:06 cmd='./parent.py'          pid=106497  pgid=106497  ppid=1652153] Goodbye

❯ pgrep child.py || echo no child left behind
no child left behind
```
