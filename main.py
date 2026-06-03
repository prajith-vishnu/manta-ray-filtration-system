import os

def initialize_system():
    print("INITIALIZING: Bio-Inspired Vortical Fluid Remediation")

    directories = ['data_fetch', 'simulations', 'prototypes']

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")

if __name__ == "__main__":
    initialize_system()
    print("System initialization complete. Ready for data fetching, simulations, and prototype development.")