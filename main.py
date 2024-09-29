from Solver import MagneticCircuitSolver
from PySide6.QtWidgets import QApplication
import sys 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Optional: Set a style for consistency
    ex = MagneticCircuitSolver()
    ex.show()
    sys.exit(app.exec())