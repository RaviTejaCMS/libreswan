/* Wrapper for <net/pfkeyv2.h>, for libreswan
 *
 * Copyright (C) 2018 Andrew Cagney
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.  See <https://www.gnu.org/licenses/gpl2.txt>.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * for more details.
 */

#ifndef LSW_PFKEYv2_H
#define LSW_PFKEYv2_H

/*
 * See: https://tools.ietf.org/html/rfc2367
 *
 * This header pulls in all the SADB_* and sadb_* declarations
 * described by RFC 2368 (along with any extensions which use the
 * prefix SADB_X_... or sadb_x_...).
 *
 * Typically this just involves including <net/pfkeyv2.h>, but on
 * linux it needs to pull in the local hacked up version of the same
 * file.

 * Why?
 *
 * the kernel_alg.[hc] code uses structures found in this header;
 * because the official version lacks some algorithm definitions (but
 * are they still needed); and linux kernel code is using the compress
 * macro values.
 */

#ifdef linux
#include "linux-pfkeyv2.h"	/* include/linux/pfkeyv2.h why? */
#else
#include <net/pfkeyv2.h>
#endif

#endif
