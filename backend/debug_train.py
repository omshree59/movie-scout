import sys, traceback
sys.path.insert(0, '.')
try:
    from ml_pipeline.train import run_training
    run_training()
except Exception as e:
    traceback.print_exc()
