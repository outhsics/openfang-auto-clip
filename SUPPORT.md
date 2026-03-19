# Support

## Where To Ask What

- Bugs: GitHub Issues
- Feature proposals: GitHub Issues or Discussions
- Usage questions: GitHub Discussions
- Security concerns: follow [SECURITY.md](SECURITY.md)

## Before Opening A Thread

Please include:

- your operating system and Python version
- whether `./auto_clip.sh --doctor` passes
- the command you ran
- the exact error output
- whether you used local media, synthetic benchmark media, or a remote URL

## Fastest Evaluation Path

If you are new to the project, start here instead of debugging a live URL first:

1. run `./auto_clip.sh --doctor`
2. run `python3 scripts/run_local_evaluation.py`
3. inspect the generated local evaluation report, benchmark assets, and Level 2 suite outputs
4. then test a real URL
