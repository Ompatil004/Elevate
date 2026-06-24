import cProfile
import pstats
import sys

def main():
    with open('test_regression_meal_engine.py', 'r') as f:
        code = compile(f.read(), 'test_regression_meal_engine.py', 'exec')
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        exec(code, globals())
    except Exception as e:
        print(f"Exception during execution: {e}")
    
    profiler.disable()
    
    stats = pstats.Stats(profiler, stream=sys.stdout)
    stats.sort_stats('cumtime')
    stats.print_stats(30)

if __name__ == "__main__":
    main()
