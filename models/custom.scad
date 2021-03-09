//----------------------------------------------
// Custom Support size must be 1x1x1 
//----------------------------------------------
$fn=30;

translate([-0.5,-0.5,-1.0]) 
union() {
    translate([0.5,0.55,0.0]) rotate([90, 0, 0]) {
			linear_extrude(height=0.1) {
				polygon(points=[[-0.65,0],[-1.18,0],[-1,0.4],[-0.05,1],[0.05,1],[0.05,0.95],[-0.35,0.5]], convexity=1);
			}
		}
    translate([-0.4,0.5,0.0]) cylinder ( h = 0.02, r = 0.3, center = false);
}
