# Problem

The position of celestial objects in the sky is often expressed in Alt-Azimuthal coordinates.
When we setup a dobsonian for observation, its position wrt. the Alt-Az coordinate system is unknown. For example:
- its base is not perfectly horizontal because of the nature of terrain.
- the optical tube (OTA) does not point towards North
- the OTA inclination is unknown because we are using optical encoders.

We can introduce reference frames for each telescope part involved. For example, we can have a reference frame for the telescope base and describe its tilt wrt the horizon (i.e. the Alt-Az system) through a (unknown) change of basis matrix.
Using a set of pairs (star Alt-Az coordinates, telescope angles), we can determine the change of basis matrices corresponding to the current telescope orientation. Once these have been determined, we can translate Alt-Az position of celestial objects into telescope angles, and guide the user towards the object.


# Reference frames

All reference frames are right handed: $z=x \times y$. Rotations are oriented according to the right hand rule.

- $S_{O}$: alt-az coordinate system. $z_{S_{O}}$ points towards the sky, $x_{S_{O}}$ points towards the North. The alt-az angles are measured wrt to the vector $\mathbf{i}=[1, 0, 0]$ of this frame.
- $S_{azO}$: This RF corresponds to the telescope base plane. Fixed wrt. $S_{O}$ (unless we move the base!). We'll indicate with $z_{S_{azO}}$ the axis orthogonal to the base plane. We assume $\langle z_{S_{O}},z_{S_{azO}}\rangle > 0$. Other than this, the coordinates of $S_{azO}$ wrt $S_{O}$ are unknown.
- $S_{az}$: This RF corresponds to the telescope horizontal rotating plane. We have $z_{S_{az}}=z_{S_{azO}}$. Initially, $S_{az}=S_{azO}$.
- $S_{tilt}$: This RF corresponds to $S_{az}$ tilted about $x_{S_{az}}$ by an unknown, small angle. We thus have $x_{S_{tilt}}=x_{S_{az}}$. This models alignment errors between the horizontal rotating plane and the (horizontal-ish) axis of vertical rotation.
- $S_{altO}$: This RF corresponds to the unknown initial rotation about axis $y_{S_{tilt}}$, i.e. the optical axis altitude when the telescope is started.
- $S_{alt}$: This RF corresponds to the telescope's vertical rotating plane. We have $y_{S_{alt}}=y_{S_{altO}}$. Initially, $S_{alt}=S_{altO}$. The vector $x_{S_{alt}}$ corresponds to the optical axis.

# Change of basis matrices

$R^{[azO]}$ This is the transformation $S_{O} \to S_{azO}$. We assume no prior information about this matrix, other than it's orthogonal. We'll just model it with 9 parameters:
$$
R ^{[azO]}_{\theta}=(\theta_{ij})^{\top}\quad i,j=1\dots3
$$
$R^{[az]}$: This is a transformation about $z_{S_{az}}$ by a known angle (measured by a sensor). It takes the form:
$$
R^{[az]}(\alpha)=\begin{bmatrix}
\cos \alpha & -\sin \alpha & 0 \\
\sin \alpha & \cos \alpha & 0  \\
0 & 0 & 1
\end{bmatrix}^{\top}
$$
$R^{[tilt]}_{\theta}$: This is the transformation about $x_{S_{az}}$ by an unknown, small angle. Since we are not interested in the angle itself, we'll model it with two unknown parameters $\theta_{1},\theta_{2}$:
$$
R^{[tilt]}_{\theta}=\begin{bmatrix}
1 & 0 & 0 \\
0 & \theta_{1} & -\theta_{2} \\
0 & \theta_{2} & \theta_{1} \\
\end{bmatrix}^{\top}
$$
$R^{[altO]}$: This is the transformation about $y_{S_{tilt}}$ by an unknown angle corresponding to the initial altitude of the telescope. It takes the form:
$$
R^{[altO]}_{\theta}=\begin{bmatrix}
\theta_{3}& 0 & \theta_{4} \\
0 & 1 & 0 \\
-\theta_{4} & 0 & \theta_{3} \\
\end{bmatrix}^{\top}
$$
$R^{[alt]}$: This is the transformation about $y_{S_{altO}}$ by a known angle (measured by a sensor). It takes the form:
$$
R^{[alt]}(\beta)=\begin{bmatrix}
\cos \beta& 0 & \sin \beta \\
0 & 1 & 0 \\
-\sin \beta & 0 & \cos \beta \\
\end{bmatrix}^{\top}
$$
# Initial state estimation

## Basic problem statement

During alignment, a stellar object $s_{i}^{[0]}$ in $S_{O}$ coordinates will be aligned with the optical axis. In other words, the vector with alt-az coordinates $s_{i}$ will correspond with the vector $\mathbf{i}=[1,0,0]$ in $s_{alt}$ coordinates by rotating the telescope by angles $\alpha_{i},\beta_{i}$.

For a given point $s_{i}$, we'll define the alignment error as:
$$
e(s_{i})=|t-R^{[alt]}(\beta)R^{[altO]}_{\theta}R^{[tilt]}_{\theta}R^{[az]}(\alpha)R ^{[azO]}_{\theta}s_{i}|^{2}
$$
We then want to find the vector $\theta$ that satisfies:
$$
\begin{dcases}
\theta &=\arg \min_{\theta} \sum_{i=1}^n \frac{e(s_{i})}{n} \\
 R^{[azO]}R^{[azO]T} &= I\\
R^{[tilt]}R^{[tilt]T} &= I\\
R^{[altO]}R^{[altO]T} &= I\\
\end{dcases}
$$
where the constraints impose that the transformation matrices are orthonormal. 
I'm dividing the squared error by $n$ so that the overall error does not depend on the number of points, which simplifies adding regularization terms.
In all I have 13 parameters to estimate.

## Regularization

We'll add regularization terms $reg_{tilt}, reg_{azO}$ meant to privilege small angles (the tilt is small and the telescope is almost horizontal). This is done to discourage the selection of implausible setups (e.g. $tilt + \pi$).

In $reg_{tilt}$ case, the rotation matrix $(R^{[tilt]})^T$ describes a rotation about $x_{Saz}$, so I impose that $\|\mathbf{j} - (R^{[tilt]})^{\top}\mathbf{j}\|^{2}$ is small. If the real $tilt$ is $5$ degrees, this corresponds to a penalty of 0.0076. For 3 degrees we get 0.0027. The impact of this regularization on the accuracy should thus be negligible.

For $reg_{azO}$, we want that the $z_{azO}$ axis is "paired" to the $z_{S_{O}}$ axis. We'll express this by requiring that $\|\mathbf{k} - (R^{[azO]})^T\mathbf{k}\|^{8}$. In this case, a misalignment of 20 degrees (which is unrealistically large) gets a negligible penalty of 0.0002.

## Final problem form

$$
\begin{dcases}
\theta &=\arg \min_{\theta} \sum_{i=1}^n \frac{e(s_{i})}{n} + \|\mathbf{j} - (R^{[tilt]})^T\mathbf{j}\|^{2} + \|\mathbf{k} - (R^{[azO]})^T\mathbf{k}\|^{8}\\
 R^{[azO]}R^{[azO]T} &= I\\
R^{[tilt]}R^{[tilt]T} &= I\\
R^{[altO]}R^{[altO]T} &= I\\
\end{dcases}
$$

I'll "enforce" the constraints by adding penalty terms of the form:
$$
p\cdot((R^{[azO]}R^{[azO]T}-I)_{ij})^{2}\quad i,j=1,2,3
$$
# Derive telescope angles given Alt-az coordinates

The alignment procedure determines matrices such that, when the telescope points to an object of coordinates $s$, with its angles measuring $\alpha, \beta$, we have:
$$
\mathbf{i}=R^{[alt]}(\beta)R^{[altO]}_{\theta}R^{[tilt]}_{\theta}R^{[az]}(\alpha)R ^{[azO]}_{\theta}s
$$
which can be rewritten as:
$$
\begin{align}
{R^{[altO]}_{\theta}}^{\top}{R^{[alt]}(\beta)}^{\top}\mathbf{i}=R^{[tilt]}_{\theta}R^{[az]}(\alpha)R ^{[azO]}_{\theta}s & & (1)
\end{align}
$$
This is a linear system in the unknowns $\cos \alpha, \sin \alpha, \cos \beta, \sin \beta$. It can be seen (use `sympy`) that the left side of $(1)$ evaluates to:
$$
\begin{align}

{R^{[altO]}_{\theta}}^{\top}{R^{[alt]}(\beta)}^{\top}\mathbf{i} = \left[\begin{matrix}t_{3} talt_{cos} - t_{4} talt_{sin}\\0\\- t_{3} talt_{sin} - t_{4} talt_{cos}\end{matrix}\right] & & (1)
\end{align}
$$
This allows to solve this system in two phases:
- first, we use the first equation to determine $\sin \alpha, \cos \alpha$.
- second, we substitute $\sin \alpha, \cos \alpha$ on the right side of $(1)$ to obtain the vector $R^{[tilt]}_{\theta}R^{[az]}(\alpha)R ^{[azO]}_{\theta}s$. We then solve the linear system:
    $$
    \left[\begin{matrix}t_{3} talt_{cos} - t_{4} talt_{sin}\\0\\- t_{3} talt_{sin} - t_{4} talt_{cos}\end{matrix}\right] = \left[\begin{matrix}v_{1} \\ 0\\ v_{3}\end{matrix}\right] 
    $$
    With unknowns $\cos \beta, \sin \beta$.

## Determining telescope azimuth

For second component of the vector $R^{[tilt]}_{\theta}R^{[az]}(\alpha)R ^{[azO]}_{\theta}s$ we then have:
$$
0 =
s_{1} t_{13} t_{2} + s_{2} t_{2} t_{23} + s_{3} t_{2} t_{33} + taz_{cos} \left(s_{1} t_{1} t_{12} + s_{2} t_{1} t_{22} + s_{3} t_{1} t_{32}\right) + taz_{sin} \left(- s_{1} t_{1} t_{11} - s_{2} t_{1} t_{21} - s_{3} t_{1} t_{31}\right)
$$
> [!tldr]- Code that assists with the generation of the latex expression and the python code for terms calculation
> ```python
> from sympy import print_latex
> from sympy.simplify.radsimp import collect
> from sympy.utilities.lambdify import lambdastr
> 
> expansion = collect(sp.expand((R_tilt @ R_az @ R_azO @ P)[1]), (taz_cos, taz_sin))
> print_latex(expansion)
> lambdastr((), expansion)
> ```

This is linear equation in $\cos/\sin \alpha$ that can be solved as follows:
$$
\begin{align}
A \sin \alpha + B \cos \alpha + C &= 0 \\
\sin \alpha &= -\frac{B}{A}\cos \alpha -\frac{C}{A} &(A \neq 0)\\
1-\cos ^{2}\alpha&=\frac{B^{2}}{A^{2}}\cos ^{2}\alpha + 2 \frac{BC}{A^{2}} \cos \alpha + \frac{C^{2}}{A^{2}}\\
0&=\left(\frac{B^{2}}{A^{2}} + 1\right)\cos ^{2}\alpha + 2 \frac{BC}{A^{2}} \cos \alpha + \frac{C^{2}}{A^{2}}-1\\
\cos \alpha &= -\frac{C}{B}&  (A=0)
\end{align}
$$
In general we have 2 values for $\cos \alpha$, each of them associated to 2 values for $\sin \alpha$ (via the identity $\cos ^{2}\alpha + \sin ^{2}\alpha = 1$). We thus have up to 4 distinct pairs $(\cos \alpha, \sin \alpha)$.

## Determining telescope altitude

$$
\begin{align}

talt_{\cos} &= \frac{v_{1}+t_{4}talt_{\sin}}{t_{3}} & & (t_{3}\neq 0)\\
-t_{3}talt_{\sin}-t_{4}\frac{v_{1}+t_{4}talt_{\sin}}{t_{3}}&=v_{3}\\
talt_{\sin}\left( -t_{3} - \frac{t_{4}^{2}}{t_{3}} \right) &= v_{3} + \frac{t_{4}}{t_{3}}v_{1}
\end{align}
$$
# Testing

The basic test plan would proceed as follows:
1. Randomly pick initial conditions $R^{[azO]},R^{[tilt]},R^{[altO]}$ within the specifications.
2. Pick $n\geq 3$ pairs of angles $(\alpha,\beta)$ describing the telescope orientations towards $n$ stars.
3. Using the transformation matrices, determine the $S_{az}$ coordinates of such objects
4. Use the $S_{az}$ coordinates and the $(\alpha_{i},\beta_{i})$ angles to estimate $\hat{R}^{[azO]},\hat{R}^{[tilt]},\hat{R}^{[altO]}$
5. Use the [Frobenius Norm](https://en.wikipedia.org/wiki/Matrix_norm#Frobenius_norm) to verify that $\|R^{[azO]}-\hat{R}^{[azO]}\|_{F} \approx 0$.

## Data generation

For a given $(\alpha_{i}, \beta_{i})$, we need to find an $s_{i}$ such that:
$$
R^{[alt]}(\beta_{i})R^{[altO]}_{\theta}R^{[tilt]}_{\theta}R^{[az]}(\alpha_{i})R ^{[azO]}_{\theta}s_{i} = \mathbf{j}
$$
which gives:
$$
s_{i} = R ^{[azO]T}_{\theta} R^{[az]T}(\alpha_{i}) R^{[tilt]T}_{\theta} R^{[altO]T}_{\theta} R^{[alt]T}(\beta_{i})\mathbf{j}
$$


# Implementation notes

I'll use `sympy` to derive the Lagrangian's gradient equations. I'll convert them in python code to speed-up execution and avoid depending on `sympy` at runtime ( #todo verify if this is possible).

I'll have terms for:
$$
\begin{align}
\frac{ \partial e(s_{i}) }{ \partial \theta_{ij} }& & i,j&=1,2,3\\
\frac{ \partial e(s_{i}) }{ \partial \theta_{i} } & & i&=1\dots 4\\
\frac{ \partial \|\mathbf{i} - (R^{[tilt]})^T\mathbf{i}\|^{2} }{ \partial \theta_{i} } & & i & =1,2 \\
\frac{ \partial \|\mathbf{k} - (R^{[azO]})^T\mathbf{k}\|^{8}}{ \partial \theta_{ij} }& & i,j&=1,2,3\\
\end{align}
$$
Note that the first two groups of terms also depend on the coordinates $s_{i}$, so I must to represent $R^{[az]},R^{[alt]}$ as `sympy` matrices in order to generate code that can take $s_{i}$ as parameters.

