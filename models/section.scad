//----------------------------------------------
// Section Support 
// Size must be 1 mm height ! 
//----------------------------------------------
$fn=40;

translate([-0.5,-0.5,-0.5]) 
union() {
    translate([0.5,0.5,0.0]) cube([0.1,0.99,1], center = true);
    translate([0.5,0.5,-0.25]) cylinder(h=0.5, r1=0.5, r2=0, center = true);
}
