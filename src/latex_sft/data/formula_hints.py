"""Frozen historical name shortcuts used to identify underspecified inputs."""

FORMULA_NAME_SHORTCUTS: dict[str, str] = {
    "Mean Squared Error": "MSE loss",
    "Cross-Entropy Loss": "cross entropy loss",
    "Softmax Function": "softmax formula",
    "Bayes' Theorem": "Bayes formula",
    "Gaussian Integral": "gaussian integral",
    "Euler's Formula": "Euler formula",
    "ReLU Activation Function": "ReLU",
    "Gradient Descent Update": "GD update",
    "Hessian Matrix": "Hessian matrix",
    "Jacobian Matrix": "Jacobian matrix",
    "Kinematic Velocity Equation": "velocity update formula",
    "Kinematic Displacement Equation": "displacement formula",
    "Rotation Matrix": "rotation matrix",
    "Diagonal Matrix": "diagonal matrix",
    "Laplace Transform": "Laplace transform",
    "Ampere-Maxwell Law": "Ampere-Maxwell law",
    "Complex Conjugate Product": "complex conjugate product",
    "De Broglie Wavelength": "de Broglie wavelength",
    "Binomial Theorem": "binomial theorem",
    "Characteristic Equation": "characteristic equation",
    "Schrodinger Equation": "Schrodinger equation",
}


AMBIGUOUS_SHORTCUT_CONTEXT: dict[str, str] = {
    "Kinematic Displacement Equation": "displacement formula with v0 a delta x",
    "Kinematic Velocity Equation": "velocity formula with v0 a t",
    "Laplace Transform": "Laplace transform integral from 0 to infinity",
    "Hessian Matrix": "Hessian second partial matrix",
    "Jacobian Matrix": "Jacobian partial derivative matrix",
    "Covariance": "covariance formula for x and y",
    "Characteristic Equation": "det A minus lambda I equals 0",
    "Product Rule": "product rule derivative",
    "Softmax Function": "softmax exp over sum exp",
    "Schrodinger Equation": "Schrodinger equation i hbar d psi dt",
}
