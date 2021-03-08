//----------------------------------------------
// Custom Support size must be 1x1x1 
//----------------------------------------------
$fn=30;

translate([-0.5,-0.5,-1.0]) 
union() {
    translate([0.2,0.5,0.0]) cylinder ( h = 0.01, r = 0.3, center = false);
    translate([0.5,0.5,0.96]) sphere ( r = 0.05);
    translate([0.13,0.5,0.01]) cylinder ( h = 0.7, r1 = 0.2, r2 = 0.14, center = false);
    translate([0.13,0.5,0.7]) sphere ( r = 0.14);
    translate([0.5,0.5,0.96]) rotate(-125,[0,1,0]) cylinder ( h = 0.4, r1 = 0.05, r2 = 0.12, center = false);
}
