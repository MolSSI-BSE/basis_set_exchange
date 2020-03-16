.. _dunningmod:

Modifications to Dunning-style basis sets
==============================================


The Dunning-style aug-cc basis sets can be modified in two ways. The first is by
extending the augmentation, as described by Woon & Dunning (https://dx.doi.org/10.1063/1.466439).
The second is by removing diffuse functions, forming the 'calendar' basis sets
(Papajak & Truhlar, https://dx.doi.org/10.1021/ct1005533)


Extending the augmentation
--------------------------

The diffuse functions present in the aug-cc basis sets can extended via a simple
algorithm, forming the d-aug, t-aug, q-aug (etc) basis sets.

First, two parameters (alpha and beta) are found for each angular momentum,
based on the existing exponents - alpha is the smallest (most diffuse) exponent
in the aug-cc basis set, and beta is the ratio of the two smallest exponents (and is <1).

Then, the new exponents are generated from alpha and beta. The d-aug exponent
is alpha*beta, the t-aug alpha*beta^2, and q-aug alpha*beta^3.

This functionality is implemented in the :func:`basis_set_exchange.manip.extend_dunning_aug` function.

Take, for example, He/aug-cc-pVTZ::

    BASIS "ao basis" PRINT
    #BASIS SET: (7s,3p,2d) -> [4s,3p,2d]
    He    S
          2.340000E+02           2.587000E-03           0.000000E+00           0.000000E+00           0.00000000
          3.516000E+01           1.953300E-02           0.000000E+00           0.000000E+00           0.00000000
          7.989000E+00           9.099800E-02           0.000000E+00           0.000000E+00           0.00000000
          2.212000E+00           2.720500E-01           0.000000E+00           0.000000E+00           0.00000000
          6.669000E-01           4.780650E-01           1.000000E+00           0.000000E+00           0.00000000
          2.089000E-01           3.077370E-01           0.000000E+00           1.000000E+00           0.00000000
          0.0513800              0.00000000             0.00000000             0.00000000             1.0000000
    He    P
          3.044000E+00           1.000000E+00           0.000000E+00           0.00000000
          7.580000E-01           0.000000E+00           1.000000E+00           0.00000000
          0.1993000              0.00000000             0.00000000             1.0000000
    He    D
          1.965000E+00           1.0000000              0.00000000
          0.4592000              0.00000000             1.0000000
    END


The parameters are generated as below:

+----------------+--------------------+--------------------+--------------------+
|                | **S**              | **P**              | **D**              |
+----------------+--------------------+--------------------+--------------------+
| Smallest       | 2.089000E-01       | 7.580000E-01       | 1.965000E+00       |
| Exponents      +--------------------+--------------------+--------------------+
|                | 0.0513800          | 0.1993000          | 0.4592000          |
+----------------+--------------------+--------------------+--------------------+
| alpha          | 5.1380E-02         | 1.9930E-01         | 4.5920E-01         |
+----------------+--------------------+--------------------+--------------------+
| beta           | 2.459550E-01       | 2.629288E-01       | 2.336896E-01       |
+----------------+--------------------+--------------------+--------------------+
| d-aug exponent | 1.2637E-02         | 5.2402E-02         | 1.0731E-01         |
+----------------+--------------------+--------------------+--------------------+
| t-aug exponent | 3.1082E-03         | 1.3778E-02         | 2.5077E-02         |
+----------------+--------------------+--------------------+--------------------+
| q-aug exponent | 7.6447E-04         | 3.6226E-03         | 5.8603E-03         |
+----------------+--------------------+--------------------+--------------------+

Therefore, He/q-aug-cc-pVTZ will be::

    BASIS "ao basis" PRINT
    #BASIS SET: (7s,3p,2d) -> [4s,3p,2d]
    He    S
          2.340000E+02           2.587000E-03           0.000000E+00           0.000000E+00           0.00000000
          3.516000E+01           1.953300E-02           0.000000E+00           0.000000E+00           0.00000000
          7.989000E+00           9.099800E-02           0.000000E+00           0.000000E+00           0.00000000
          2.212000E+00           2.720500E-01           0.000000E+00           0.000000E+00           0.00000000
          6.669000E-01           4.780650E-01           1.000000E+00           0.000000E+00           0.00000000
          2.089000E-01           3.077370E-01           0.000000E+00           1.000000E+00           0.00000000
          0.0513800              0.00000000             0.00000000             0.00000000             1.0000000
    He    S
          1.264E-02              1.0
    He    S
          3.108E-03              1.0
    He    S
          7.645E-04              1.0
    He    P
          3.044000E+00           1.000000E+00           0.000000E+00           0.00000000
          7.580000E-01           0.000000E+00           1.000000E+00           0.00000000
          0.1993000              0.00000000             0.00000000             1.0000000
    He    P
          5.240E-02              1.0
    He    P
          1.378E-02              1.0
    He    P
          3.623E-03              1.0
    He    D
          1.965000E+00           1.0000000              0.00000000
          0.4592000              0.00000000             1.0000000
    He    D
          1.073E-01              1.0
    He    D
          2.508E-02              1.0
    He    D
          5.860E-03              1.0


Papajak/Truhlar 'Calendarization'
---------------------------------

Diffuse functions can also be removed from the aug-cc basis sets. Doing
so results in the Truhlar 'calendar' basis sets. The names derive from the
fact that 'aug' (for 'augmented') is also the abbreviation for the month of
August. Removing diffuse functions moves you earlier into the year - 'jul',
'jun', etc, progressively have fewer diffuse functions.
'jul' basis sets are sometimes referred to as 'heavy-aug'.

This procedure can apply to all sorts of aug-cc basis sets (aug-cc-pVTZ,
aug-cc-pV(T+d)Z, aug-cc-pCVTZ, etc).

To form the earlier months, the procedure is as follows

  1. 'jul' - remove all diffuse functions on H and He
  2. 'jun' - remove the diffuse function from the highest AM from non-H,He elements
  3. 'may' - remove the diffuse function from the next highest AM from non-H,He elements
  4. Continue until finished or you hit 'jan'

In Papajak & Truhlar (2011, https://dx.doi.org/10.1021/ct1005533), truncation
of the diffuse functions stops when only s & p diffuse functions remain. This
month is also denoted 'maug' (minimally-augmented).

Also in that paper, Papajak & Truhlar developed their method for basis sets
that did not apply past Ar. However, according to Truhlar (via personal
communication), this method can be applied to all elements, including
transition metals. In that case, the 'maug' basis sets will contain s, p,
and d diffuse functions on transition metals, and s and p diffuse functions
on all other non-H,He elements.

However, you may remove those diffuse functions as well. In Gaussian, these
are denoted as 't(month)' basis sets (tjul, tjun, etc). These basis sets are
equivalent to the regular '(month)' basis sets until you reach maug (spd on
transition metals, sp on other elements except H,He). In the BSE, we adopt
the nomenclature whereby you can move earlier into the year, without the
't' prefix.

This functionality is implemented in the
:func:`basis_set_exchange.manip.truhlar_calendarize` function.

Below is a table for aug-cc-pV{D,T,Q}Z that can be taken as representative
(although, as noted above, this procedure applies to many more basis sets)

+----------------+--------------+-----------+---------------+---------------+
|                |              |               **month-cc-pVXZ**           |
+                +              +-----------+---------------+---------------+
| **Base**       | **Month**    | H,He      | Li-Ar,Ga-Kr   | Sc-Zn         |
+----------------+--------------+-----------+---------------+---------------+
| aug-cc-pVDZ    | aug          | *sp*      | *spd*         | *spdf*        |
|                +--------------+-----------+---------------+---------------+
|                | jul          |           | *spd*         | *spdf*        |
|                +--------------+-----------+---------------+---------------+
|                | jun (maug)   |           | *sp*          | *spd*         |
|                +--------------+-----------+---------------+---------------+
|                | may          |           | *s*           | *sp*          |
|                +--------------+-----------+---------------+---------------+
|                | apr          |           |               | *s*           |
+----------------+--------------+-----------+---------------+---------------+
| aug-cc-pVTZ    | aug          | *spd*     | *spdf*        | *spdfg*       |
|                +--------------+-----------+---------------+---------------+
|                | jul          |           | *spdf*        | *spdfg*       |
|                +--------------+-----------+---------------+---------------+
|                | jun          |           | *spd*         | *spdf*        |
|                +--------------+-----------+---------------+---------------+
|                | may (maug)   |           | *sp*          | *spd*         |
|                +--------------+-----------+---------------+---------------+
|                | apr          |           | *s*           | *sp*          |
|                +--------------+-----------+---------------+---------------+
|                | mar          |           |               | *s*           |
+----------------+--------------+-----------+---------------+---------------+
| aug-cc-pVQZ    | aug          | *spdf*    | *spdfg*       | *spdfgh*      |
|                +--------------+-----------+---------------+---------------+
|                | jul          |           | *spdfg*       | *spdfgh*      |
|                +--------------+-----------+---------------+---------------+
|                | jun          |           | *spdf*        | *spdfg*       |
|                +--------------+-----------+---------------+---------------+
|                | may          |           | *spd*         | *spdf*        |
|                +--------------+-----------+---------------+---------------+
|                | apr (maug)   |           | *sp*          | *spd*         |
|                +--------------+-----------+---------------+---------------+
|                | mar          |           | *s*           | *sp*          |
|                +--------------+-----------+---------------+---------------+
|                | feb          |           |               | *s*           |
+----------------+--------------+-----------+---------------+---------------+
