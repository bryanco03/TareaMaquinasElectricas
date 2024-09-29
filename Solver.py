from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QTextEdit,
                               QComboBox, QSpacerItem, QMessageBox,QCheckBox,
                               QRadioButton, QButtonGroup)
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtCore import Qt
import sys
from circuitoMagnetico import (calcularI2Tabla, calcularI2Ecuacion, 
                              calcularI1Ecuacion, calcularI1Tabla, 
                              deformacion)
class MagneticCircuitSolver(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Magnetic Circuit Solver')
        self.setGeometry(100, 100, 600, 600)

        layout = QVBoxLayout()

        # Layout principal vertical
        self.layout = QVBoxLayout()

        # Selector de parámetro a ingresar: I1 o I2
        radio_layout = QHBoxLayout()
        self.radio_i1 = QRadioButton("Ingresar I1")
        self.radio_i2 = QRadioButton("Ingresar I2")
        self.radio_i1.setChecked(True)  # Por defecto, I1 estará habilitado
        # Añadir radio buttons al grupo para que solo se pueda seleccionar uno
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_i1)
        self.radio_group.addButton(self.radio_i2)

        # Conectar los radio buttons para habilitar/deshabilitar los campos
        self.radio_i1.toggled.connect(self.toggle_inputs)

        radio_layout.addWidget(self.radio_i1)
        radio_layout.addWidget(self.radio_i2)
        layout.addLayout(radio_layout)


        # Input fields
        main_input_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()


        int_positive_validator = QIntValidator(0, 100000000)
        
        factor_apilado_validator = QDoubleValidator(0,1,3)

        positive_validator = QDoubleValidator(0.000000001, 1e20, 9)  # Min: 0.01, Max: large value, 2 decimals

        self.inputs = {}
        all_inputs = ['N1', 'N2', 'I1', 'I2', 'Factor_apilado', 'S_L', 'S_c', 
                      'A', 'L1', 'L2', 'L3', 'L_E', 'Phi_E']

        for i, input_name in enumerate(all_inputs):
            field_layout = QHBoxLayout()
            label = QLabel(f"{input_name}:")
            field_layout.addWidget(label)
            self.inputs[input_name] = QLineEdit()

            # Apply validator to restrict input to strictly positive numbers for specific fields
            if input_name in ['S_L','S_c', 'A', 'L1', 'L2', 'L3', 'L_E']:
                self.inputs[input_name].setValidator(positive_validator)
            elif input_name in ['N1', 'N2']:
                self.inputs[input_name].setValidator(int_positive_validator)
            elif input_name == 'Factor_apilado':
                self.inputs[input_name].setValidator(factor_apilado_validator)

            else:
                # Allow any number for fields that don't require strictly positive validation
                self.inputs[input_name].setValidator(QDoubleValidator())


            field_layout.addWidget(self.inputs[input_name])
            if i < len(all_inputs) // 2:
                left_layout.addLayout(field_layout)
            else:
                right_layout.addLayout(field_layout)
        # Hacer que I2 esté deshabilitado por defecto
        self.inputs['I2'].setEnabled(False)


        main_input_layout.addLayout(left_layout)
        main_input_layout.addLayout(right_layout)
        layout.addLayout(main_input_layout)

                # Checkboxes for considering dispersion coefficient and deformation percentage
        self.dispersion_checkbox = QCheckBox("Considerar coeficiente de dispersión")
        self.deformation_checkbox = QCheckBox("Considerar porcentaje de deformación del área")
        
        # Layouts for the optional inputs
        self.dispersion_input = QLineEdit()
        self.deformation_input = QLineEdit()

        self.dispersion_input.setValidator(QDoubleValidator())
        self.deformation_input.setValidator(QDoubleValidator())

        # Initially hide the input fields
        self.dispersion_input.setVisible(False)
        self.deformation_input.setVisible(False)
        
        # Set default placeholders and values (invisible inputs will be 1 by default)
        self.dispersion_input.setPlaceholderText("Coeficiente de dispersión ")
        self.deformation_input.setPlaceholderText("Porcentaje de deformación (ej. 5%)")

        # Connect checkboxes to show/hide inputs
        self.dispersion_checkbox.stateChanged.connect(self.toggle_dispersion_input)
        self.deformation_checkbox.stateChanged.connect(self.toggle_deformation_input)

        # Add checkboxes and inputs to the layout
        layout.addWidget(self.dispersion_checkbox)
        layout.addWidget(self.dispersion_input)
        layout.addWidget(self.deformation_checkbox)
        layout.addWidget(self.deformation_input)



        # H-B curve input
        hb_layout = QHBoxLayout()
        hb_layout.addWidget(QLabel("Curva H-B:"))
        self.hb_type = QComboBox()
        self.hb_type.addItems(['Ecuacion', 'Tabla'])
        hb_layout.addWidget(self.hb_type)
        layout.addLayout(hb_layout)

        # Dynamic layout for H-B values or equation (based on user selection)
        self.hb_dynamic_layout = QVBoxLayout()
        layout.addLayout(self.hb_dynamic_layout)
        
        # Connect signal to show H-B table inputs or equation when type is selected
        self.hb_type.currentIndexChanged.connect(self.show_hb_inputs)

        # Button to add new H-B row (only visible for Table option)
        self.add_row_button = QPushButton("Añadir fila H-B ")
        self.add_row_button.clicked.connect(self.add_hb_row)
        self.add_row_button.setVisible(False)  # Initially hidden
        layout.addWidget(self.add_row_button)

        # Spacer for dynamic content
        self.spacer = QSpacerItem(20, 40)
        layout.addSpacerItem(self.spacer)

        self.instructions_button = QPushButton('Mostrar Instrucciones', self)
        self.instructions_button.clicked.connect(self.show_instructions)
        layout.addWidget(self.instructions_button)


        # Calculate button
        self.calc_button = QPushButton('Calcular')
        self.calc_button.clicked.connect(self.calculate)
        layout.addWidget(self.calc_button)

        # Results display
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        layout.addWidget(self.results)

        self.setLayout(layout)


    def toggle_inputs(self):
        """
        Habilitar y deshabilitar campos de entrada en función de la selección.
        """
        if self.radio_i1.isChecked():
            self.inputs['I1'].setEnabled(True)
            self.inputs['I2'].setEnabled(False)
            self.inputs['I2'].clear()  # Limpiar el valor de I2 cuando esté deshabilitado
        else:
            self.inputs['I1'].setEnabled(False)
            self.inputs['I1'].clear()  # Limpiar el valor de I1 cuando esté deshabilitado
            self.inputs['I2'].setEnabled(True)

    def show_hb_inputs(self):
        """Show or hide the H-B input fields or equation based on the selection."""
        self.clear_hb_dynamic_layout()  # Clear any previous inputs

        if self.hb_type.currentText() == "Tabla":
            # Show the "Add H-B Row" button for Table option
            self.add_row_button.setVisible(True)
        else:
            # Hide the "Add H-B Row" button when Equation is selected
            self.add_row_button.setVisible(False)

            # Add input fields for the equation constants a and b
            self.a_label = QLabel("Constante a:")
            self.a_input = QLineEdit()
            self.a_input.setPlaceholderText("Ingresar constante a")
            self.a_input.setValidator(QDoubleValidator())  # Only allow numbers
            self.hb_dynamic_layout.addWidget(self.a_label)
            self.hb_dynamic_layout.addWidget(self.a_input)

            self.b_label = QLabel("Constante b:")
            self.b_input = QLineEdit()
            self.b_input.setPlaceholderText("Ingresar constante b")
            self.b_input.setValidator(QDoubleValidator())  # Only allow numbers
            self.hb_dynamic_layout.addWidget(self.b_label)
            self.hb_dynamic_layout.addWidget(self.b_input)

    def clear_hb_dynamic_layout(self):
        """Clear all dynamically added H-B input rows or equation."""
        while self.hb_dynamic_layout.count():
            item = self.hb_dynamic_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Si el item es un layout anidado, limpiarlo también
                self.clear_layout(item.layout())
    def clear_layout(self, layout):
        """Clear all widgets from a nested layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())


    def add_hb_row(self):
        """Add a new row for entering H and B values."""
        row_layout = QHBoxLayout()

        h_input = QLineEdit()
        h_input.setPlaceholderText("H value")
        h_input.setValidator(QDoubleValidator())  # Only allow numbers
        row_layout.addWidget(h_input)

        b_input = QLineEdit()
        b_input.setPlaceholderText("B value")
        b_input.setValidator(QDoubleValidator())  # Only allow numbers
        row_layout.addWidget(b_input)

        # Add delete button to remove the row
        delete_button = QPushButton("Eliminar")
        delete_button.clicked.connect(lambda: self.delete_hb_row(row_layout))
        row_layout.addWidget(delete_button)

        self.hb_dynamic_layout.addLayout(row_layout)

    def delete_hb_row(self, row_layout):
        """Remove a specific H-B row."""
        while row_layout.count():
            child = row_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.hb_dynamic_layout.removeItem(row_layout)


    def toggle_dispersion_input(self, state):
        """Show/hide dispersion coefficient input based on checkbox state."""
        if state == Qt.Checked:
            self.dispersion_input.setVisible(True)
        else:
            self.dispersion_input.setVisible(False)

    def toggle_deformation_input(self, state):
        """Show/hide deformation percentage input based on checkbox state."""
        if state == Qt.Checked:
            self.deformation_input.setVisible(True)
        else:
            self.deformation_input.setVisible(False)

    def obtener_valores(self):
        valores = {}
        try:
            for key, input_field in self.inputs.items():
                if input_field.validator():  # Si el campo tiene un validador
                    if isinstance(input_field.validator(), QIntValidator):  # Si es un entero
                        valores[key] = int(input_field.text() or 0)  # Convertir a entero, 0 si está vacío
                    elif isinstance(input_field.validator(), QDoubleValidator):  # Si es un decimal
                        valores[key] = float(input_field.text() or 0.0)  # Convertir a flotante, 0.0 si está vacío
            # Obtener los valores opcionales de coeficiente de dispersión y porcentaje de deformación
            valores["dispersion"] = float(self.dispersion_input.text() or 1.0)
            valores["deformacion"] = float(self.deformation_input.text() or 1.0)
        except ValueError:
            self.results.append("Error: Ingrese valores numéricos válidos.")
        return valores
    
    def show_instructions(self):
        # Crear una instancia de QMessageBox
        msg_box = QMessageBox()

        # Establecer el título del pop-up
        msg_box.setWindowTitle('Instrucciones')

        # Usar HTML para agregar texto e imagen
        image_path = "circuito.png"  # Cambia esto a la ruta de tu imagen
        html_content = f"""
        <h3>Instrucciones del Programa</h3>
        <p>Estas son las instrucciones para usar el programa:</p>
        <ol>
            <li>Ingrese los valores requeridos en los campos.</li>
            <li>Presione el botón de calcular para obtener los resultados.</li>
            <li>Los valores ingresados deben estar en las unidades SI.</li>
            <li>Se debe utilizar el separador decimal una como ",".</li>
        </ol>
        <p><img src="{image_path}" width="600"></p>
        """
        
        # Establecer el contenido del mensaje como HTML
        msg_box.setTextFormat(Qt.RichText)  # Indicar que el texto está en formato HTML
        msg_box.setText(html_content)

        # Mostrar el pop-up
        msg_box.exec()


    def calculate(self):
        """Calculate and display the results based on user inputs."""
        error_message = ""
        result = ""
        try:
            N1 = int(self.inputs['N1'].text().replace(',', '.') or 0)
            N2 = int(self.inputs['N2'].text().replace(',', '.') or 0)
            phi3 = float(self.inputs['Phi_E'].text().replace(',', '.') or 0.0)
            Sl = float(self.inputs['S_L'].text().replace(',', '.') or 0.0)
            Sc = float(self.inputs['S_c'].text().replace(',', '.') or 0.0)
            fap = float(self.inputs['Factor_apilado'].text().replace(',', '.') or 0.0)
            if fap < 0 or fap > 1 :
                error_message += "El valor del factor de apilamiento debe ser entre 0 y 1\n"
            Lg = float(self.inputs['L_E'].text().replace(',', '.') or 0.0)
            L3 = float(self.inputs['L3'].text().replace(',', '.') or 0.0)
            if L3 < Lg:
                error_message += "El valor del Lg debe ser menor que L_3\n"
            L1 = float(self.inputs['L1'].text().replace(',', '.') or 0.0)
            L2 = float(self.inputs['L2'].text().replace(',', '.') or 0.0)
            A = float(self.inputs['A'].text().replace(',', '.') or 0.0)
            dispersion = float(self.dispersion_input.text().replace(',', '.') or -1.0)
            defor = float(self.deformation_input.text().replace(',', '.') or -1.0)
            if defor == -1 :
                coef = deformacion(Lg, Sc)
            elif 0 < defor < 1:
                coef = 1 + defor
            else:                                           
                error_message += "El valor del porcentaje de deformacion de area  debe ser entre 0 y 1\n"
            if dispersion == -1:
                v = 1
            elif  dispersion > 1.3 or dispersion < 1.1:
                error_message += "El valor del coeficiente de dispersion debe ser entre 1,1 y 1,3\n"
            else:
                v = dispersion

            
            if error_message:
                self.show_error_message(error_message)
            else:

                if self.hb_type.currentText() == "Tabla":
                    # Obtener H y B desde el layout dinámico
                    H = []
                    B = []
                    for i in range(self.hb_dynamic_layout.count()):
                        row_layout = self.hb_dynamic_layout.itemAt(i).layout()
                        h_value = float(row_layout.itemAt(0).widget().text().replace(',', '.') or 0.0)
                        b_value = float(row_layout.itemAt(1).widget().text().replace(',', '.') or 0.0)
                        H.append(h_value)
                        B.append(b_value)
                    if self.radio_i1.isChecked():  # Si está seleccionado ingresar I1
                        I1 = float(self.inputs['I1'].text().replace(',', '.') or 0.0)
                        if N1 > 0 and N2 > 0 and I1 > 0:
                            resultados = calcularI2Tabla(B, H, phi3, Sl, Sc, fap, Lg, L1, N1, I1, L2, N2, A, v, coef)
                            phi1 = resultados[0]
                            phi2 = resultados[1]
                            I2 = resultados[2]
                            result += f"Resultado phi1: {phi1} wb\n"
                            result += f"Resultado phi2: {phi2} wb\n"
                            result += f"Resultado I2: {I2} A\n"
                            #Mostrar los resultados
                    else:  # Si está seleccionado ingresar I2
                        I2 = float(self.inputs['I2'].text().replace(',', '.') or 0.0)
                        if N1 > 0 and N2 > 0 and I2 > 0:
                            resultados = calcularI1Tabla(H,B,I2,N2,N1,L1,L2,Sc,Sl,phi3,A,Lg,fap,v,coef)
                            phi1 = resultados[0]
                            phi2 = resultados[1]
                            I2 = resultados[2]
                            result += f"Resultado phi1: {phi1} wb\n"
                            result += f"Resultado phi2: {phi2} wb\n"
                            result += f"Resultado I1: {I2} A\n"
                else:
                    # Si el tipo es ecuación, usar constantes a y b
                    a = float(self.a_input.text().replace(',', '.') or 1.0)
                    b = float(self.b_input.text().replace(',', '.') or 1.0)
                    # Determinar si se ingresa I1 o I2 según la selección del radio button
                    if self.radio_i1.isChecked():  # Si está seleccionado ingresar I1
                        I1 = float(self.inputs['I1'].text().replace(',', '.') or 0.0)
                        if N1 > 0 and N2 > 0 and I1 > 0:
                            # Calcular I2 usando los valores de H y B de la tabla
                            resultados = calcularI2Ecuacion(a, b, phi3, Sl, Sc, fap, Lg, L1, N1, I1, L2, N2, A, v, coef)
                            phi1 = resultados[0]
                            phi2 = resultados[1]
                            I2 = resultados[2]
                            result += f"Resultado phi1: {phi1} wb\n"
                            result += f"Resultado phi2: {phi2} wb\n"
                            result += f"Resultado I2: {I2} A\n"
                    else:  # Si está seleccionado ingresar I2
                        I2 = float(self.inputs['I2'].text().replace(',', '.') or 0.0)
                        if N1 > 0 and N2 > 0 and I2 > 0:
                            resultados = calcularI1Ecuacion(a,b,I2,N2,N1,L1,L2,Sc,Sl,phi3,A,Lg,fap,v,coef)
                            phi1 = resultados[0]
                            phi2 = resultados[1]
                            I2 = resultados[2]
                            result += f"Resultado phi1: {phi1} wb\n"
                            result += f"Resultado phi2: {phi2} wb\n"
                            result += f"Resultado I1: {I2} A\n"
                # Mostrar los resultados
                self.results.append(result)

        except ValueError:
            self.results.append("Error en los valores ingresados.")




    def show_error_message(self, message):
        """Display an error message in a pop-up window."""
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setWindowTitle('Input Error')
        error_dialog.setText(message)
        error_dialog.exec()