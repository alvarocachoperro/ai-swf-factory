package com.factory.mock;

public class CalculatorTest {
    public static void main(String[] args) {
        Calculator calc = new Calculator();

        // Test add
        assert calc.add(2, 3) == 5 : "Error en el método add";

        System.out.println("✅ Todos los tests básicos pasaron correctamente.");
    }
}