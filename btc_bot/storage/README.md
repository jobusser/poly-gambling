We will have different databases for each task

storage/
├── dev.db          # your local sandbox, can be nuked freely
├── test.db         # created fresh by pytest fixtures, deleted after
└── sim.db          # paper trading — treat like production, never delete

YAML configs can change location of database