// TrueSound Probe - Vista Interna (Carcasa 2 piezas + Electrónica Unificada)

$fn = 150; 

// --- 1. COMPONENTES ELECTRÓNICOS INTERNOS ---

module modulo_microfono() {
    // Placa redonda/cuadrada del micrófono pegada a la rejilla
    color("green") {
        translate([0, 0, 4.5]) { 
            cube([14, 14, 1.5], center = true); 
            translate([0, 0, -1.5]) 
                cylinder(h = 3, r = 3, center = true); 
        }
    }
}

module electronica_unificada() {
    // Placa base (PCB) que abarca el centro y se extiende hasta el puerto
    color("darkblue") {
        translate([0, 5, 10]) cube([48, 30, 1.6], center = true);
        translate([0, 32, 10]) cube([20, 30, 1.6], center = true);
    }
    
    // Simulación de chips (CPU y módulo RF)
    color("black") translate([-10, 5, 11.5]) cube([14, 14, 2], center=true); 
    color("silver") translate([15, 5, 11.5]) cube([12, 16, 3], center=true); 
    
    // Conector RJ45 Metálico realista soldado a la PCB
    color("silver") {
        difference() {
            // Bloque exterior del conector metálico
            translate([0, 47, 16.5]) cube([16, 20, 12.5], center = true);
            
            // --- HUECO CON LA FORMA EXACTA DEL RJ45 ---
            // 1. Hueco rectangular principal
            translate([0, 48, 17.5]) cube([12.5, 22, 8.5], center = true);
            // 2. Hueco inferior central para la lengüeta
            translate([0, 48, 12.5]) cube([6.2, 22, 3], center = true);
            // 3. Rieles laterales para el clip de retención
            translate([-4.5, 48, 13]) cube([2.0, 22, 3], center = true);
            translate([4.5, 48, 13]) cube([2.0, 22, 3], center = true);
        }
    }
}

// --- 2. MÓDULOS DE CORTE Y DETALLES DE CARCASA ---

module rj45_cutout() {
    // Ventana rectangular limpia en el plástico para dejar asomar el conector metálico
    translate([0, 56, 16.5]) cube([16.5, 20.0, 13.0], center = true);
}                                                               

module ranura_redondeada() {
    hull() {
        translate([0, 0, 6.3]) rotate([0, 90, 0]) cylinder(h=16, r=1.2, center=true, $fn=36);
        translate([0, 0, -6.3]) rotate([0, 90, 0]) cylinder(h=16, r=1.2, center=true, $fn=36);
    }
}

module ranuras_perimetrales() {
    for (i = [0 : 35]) {
        angulo = i * (360 / 36);
        if (angulo < 65 || angulo > 115) {
            rotate([0, 0, angulo])
            translate([55.5, 0, 14]) 
            rotate([0, 21.8, 0]) ranura_redondeada();
        }
    }
}

module rejilla_microfono() {
    for (x = [-4 : 4]) {
        for (y = [-4 : 4]) {
            if (sqrt(x*x + y*y) <= 4.0) {
                translate([x * 4.5, y * 4.5, -1])
                    cylinder(h = 6, r = 1.3, center = false, $fn = 36);
            }
        }
    }
}

// --- 3. LAS DOS PIEZAS PRINCIPALES DE PLÁSTICO ---

module cuerpo_principal() {
    color("white", 0.3) // Transparencia para ver el interior
    difference() {
        // Cono exterior
        cylinder(h = 28, r1 = 50, r2 = 61.2, center = false);

        // Vaciado interior abierto por arriba
        difference() {
            translate([0, 0, 3.5])
                cylinder(h = 25.0, r1 = 46.5, r2 = 57.7, center = false);
                
            // Bloque macizo para el RJ45 (optimizado)
            translate([0, 55, 14.5])
                cube([19.6, 8.0, 16.0], center = true);
        }

        rejilla_microfono();
        ranuras_perimetrales();
        rj45_cutout();
    }
}

module tapa_superior() {
    color("white", 0.3) // Transparente
    union() {
        cylinder(h = 2, r = 62, center = false);
        translate([0, 0, -2.5])
            cylinder(h = 2.5, r = 57.3, center = false);
    }
}

// --- 4. ENSAMBLAJE FINAL PARA WEB ---

// La electrónica (siempre visible, placa unificada y conector realista)
modulo_microfono();
electronica_unificada();

// La carcasa (Cuerpo principal)
cuerpo_principal();

// La tapa superior (Elevada en eje Z para efecto despiece)
translate([0, 0, 32]) 
    tapa_superior();