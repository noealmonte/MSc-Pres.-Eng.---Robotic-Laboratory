= Session 3: Repeatability Evaluation (ISO 9283)

== Methodology & Statistical Formulation
According to ISO 9283, positioning repeatability $R_p$ measures the ability of the robot to return to the same commanded pose after repeated motions.

The barycenter $(bar(x), bar(y))$ of $N$ recorded positions is calculated as:
$
  bar(x) = 1/N sum_(i=1)^N x_i, quad bar(y) = 1/N sum_(i=1)^N y_i
$

The $95%$ confidence error ellipse is determined from the eigenvalues $lambda_1, lambda_2$ and eigenvectors of the sample covariance matrix $bold(Sigma)$:
$
  bold(Sigma) = 1/(N-1) sum_(i=1)^N mat(
    (x_i - bar(x))^2, (x_i - bar(x))(y_i - bar(y));
    (x_i - bar(x))(y_i - bar(y)), (y_i - bar(y))^2
  )
$

== Unidirectional Repeatability
The robot repeatedly moved between an intermediate retract pose and the target measurement pose for $N >= 50$ cycles.

== Bidirectional Repeatability
Bidirectional evaluation was conducted by approaching the target pose from two opposite directions with $N >= 25$ complete cycles (50 target approaches).

== Structural Stiffness: Folded vs. Stretched Configurations
The positioning repeatability was compared between the folded pose ${F}$ and the stretched pose ${S}$. Due to arm deflection and joint flexibilities under cantilevered loading, the stretched configuration exhibits a larger uncertainty ellipse.

== Path Following, Velocity & Corner Blending
Trajectories were commanded with varying corner blending percentages ($0\%$ to $100\%$) and Cartesian velocities ($10 "mm/s"$ to $100 "mm/s"$).
