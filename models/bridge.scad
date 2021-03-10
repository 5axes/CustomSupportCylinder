//----------------------------------------------
// Freeform Support bridge
//----------------------------------------------
$fn=20;

translate([-0.5,-0.5,-1.0]) bridge();

module bridge(){
    union() {
       translate([-0.1,0,0.0]) pilar();
       translate([1.1,1,0.0]) rotate([0, 0, 180]) pilar();
    }
}
module pilar(){
union() {
    translate([0.5,0.55,0.0]) rotate([90, 0, 0]) {
			linear_extrude(height=0.1) {
				polygon(points=[[-0.62,0],[-1.19,0],[-1,0.4],[-0.1,1],[0.1,1],[0.1,0.9],[0,0.85],[-0.45,0.4]], convexity=1);
			}
		}
    translate([-0.4,0.5,0.0]) cylinder ( h = 0.02, r = 0.3, center = false);
}
}
