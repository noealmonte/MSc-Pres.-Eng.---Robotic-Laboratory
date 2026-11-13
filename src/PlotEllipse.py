'''
MPE Control & Automation
Python function to calculate and plot an error ellipse fitting data points to 95% confidence.
@author gionata.quadri@bfh.ch
'''

import numpy as np
from matplotlib import pyplot as plt


def plotEllipse(x: list[float], y: list[float]) -> tuple[float, float, float]:
  '''
  This function calculates and plots an error ellipse fitted to 95% confidence of the x, y values given.
  Note that the ellipse will be plotted on the existing figure, otherwise a new figure will be created.

  Adapted from <https://www.visiondummy.com/2014/04/draw-error-ellipse-representing-covariance-matrix/#>

  :param list[float] x: The horizontal coordinates of the data values.
  :param list[float] y: The vertical coordinates of the data values.
  :return tuple[float, float, float]: A tuple with 3 values: The major ellipse axis, the minor ellipse axis and the orientation angle of the ellipse relative to the horizontal axis in radians.
  '''

  data = np.hstack((x, y))
  # Calculate the eigenvectors and eigenvalues
  covariance = np.cov(data, rowvar=False)
  eigenvalues, eigenvector = np.linalg.eig(covariance)
  # Get the index of the largest eigenvector
  largestEigenvalueIndices = np.argmax(eigenvalues)
  largestEigenvector = eigenvector[:, largestEigenvalueIndices]

  # Get the largest eigenvalue
  largestEigenvalue = eigenvalues.max()

  # Get the smallest eigenvector and eigenvalue
  smallestEigenvalue = eigenvalues.min()

  # Calculate the angle between the x-axis and the largest eigenvector
  angle = np.arctan2(largestEigenvector[1], largestEigenvector[0])

  # Get the coordinates of the data mean
  avg = np.mean(data, axis=0)

  # Get the 95% confidence interval error ellipse
  chiSquareValue = 2.4477
  thetaGrid = np.linspace(0, 2 * np.pi, 100)
  phi = angle
  x0 = avg[0]
  y0 = avg[1]
  a = chiSquareValue * np.sqrt(largestEigenvalue)
  b = chiSquareValue * np.sqrt(smallestEigenvalue)

  # Plot the ellipse:
  # The ellipse in x and y coordinates
  ellipseXr = np.array([a * np.cos(thetaGrid)])
  ellipseYr = np.array(b * np.sin(thetaGrid))
  # Define a rotation matrix for the ellipse angle
  R = np.array([[np.cos(phi), np.sin(phi)], [-np.sin(phi), np.cos(phi)]])

  # Rotate the ellipse
  ellipsePoints = np.transpose(np.vstack((ellipseXr, ellipseYr))) @ R

  # Plot the error ellipse
  plt.plot(ellipsePoints[:, 0] + x0, ellipsePoints[:, 1] + y0, '-g')
  return a, b, phi


if __name__ == '__main__':
  # Plot example
  # Generate the data
  s = [2, 2]
  x = np.ones((334, 1))
  import random
  x = [random.random() * val for val in x]
  y1 = np.array([random.normalvariate(s[0] * val, 1) for val in x])
  y2 = np.array([random.normalvariate(s[1] * val, 1) for val in x])

  # Plot the points
  plt.plot(y1, y2, 'r.')
  # Plot the 95% confidence ellipse
  print(plotEllipse(y1, y2))

  # Show the figure
  plt.grid(visible=True)
  plt.axis('equal')
  plt.show()
