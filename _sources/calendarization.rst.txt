.. _calendarization:

Papajak/Truhlar 'Calendarization'
=================================

Diffuse functions can be removed from the Dunning-style aug-cc basis
sets. Doing so results in the Truhlar 'calendar' basis sets (Papajak &
Truhlar, https://doi.org/10.1021/ct1005533). The names derive from
the fact that 'aug' (for 'augmented') is also the abbreviation for the
month of August. Removing diffuse functions moves you earlier into the
year - 'jul', 'jun', etc, progressively have fewer diffuse functions.
'jul' basis sets are sometimes referred to as 'heavy-aug'.

This procedure can apply to all sorts of aug-cc basis sets (aug-cc-pVTZ,
aug-cc-pV(T+d)Z, aug-cc-pCVTZ, etc).

To form the earlier months, the procedure is as follows

  1. 'jul' - remove all diffuse functions on H and He
  2. 'jun' - remove the diffuse function from the highest AM from non-H,He elements
  3. 'may' - remove the diffuse function from the next highest AM from non-H,He elements
  4. Continue until finished or you hit 'jan'

In Papajak & Truhlar (2011, https://doi.org/10.1021/ct1005533), truncation
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
