//----------------------------------------------
// Pillar Support 
// Size must be 1x1x1 
//----------------------------------------------
$fn=24;

translate([-0.5,-0.5,-0.5]) 
union() {
    translate([0.5,0.5,0.0]) cube([0.5,0.5,1.0], center = true);
    translate([0.5,0.5,-0.1]) cylinder(h=0.8, r1=0.5, r2=0.0, center = true);
}
