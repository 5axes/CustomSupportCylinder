//----------------------------------------------
// Custom Support size must be 1x1x1 
//----------------------------------------------
$fn=10;

translate([-0.5,-0.5,-0.5]) 
union() {
    translate([0.5,0.5,0.0]) cube([0.1,1,1], center = true);
    translate([0.5,0.5,0.0]) cube([1,0.1,1], center = true);
}
