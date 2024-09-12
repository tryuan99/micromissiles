#include <cmath>
#include <cstdlib>
#include <numbers>

#include "base/base.h"
#include "matplot/matplot.h"

int main(int argc, char** argv) {
  base::Init(argc, argv);

  std::vector<double> z(1000);
  std::iota(z.begin(), z.end(), std::numbers::pi / 500);
  std::vector<double> x(z.size());
  std::transform(z.cbegin(), z.cend(), x.begin(),
                 [](const double z) { return std::cos(z); });
  std::vector<double> y(z.size());
  std::transform(z.cbegin(), z.cend(), y.begin(),
                 [](const double z) { return std::sin(z); });

  auto figure = matplot::figure(/*quiet_mode=*/true);
  auto axes = matplot::gca();
  auto line = axes->plot3(x, y, z);
  axes->xlabel("x");
  axes->ylabel("y");
  axes->zlabel("z");
  figure->show();

  return EXIT_SUCCESS;
}
