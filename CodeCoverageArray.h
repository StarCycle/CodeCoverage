/*
 * CodeCoverageArray.h
 *
 *  Created on: 26 jan. 2022
 *      Author: llizhuoheng
 */

#ifndef CODECOVERAGEARRAY_H_
#define CODECOVERAGEARRAY_H_

extern unsigned char        coverageArray[];
#define CodeCount(label)    coverageArray[label/8] |= 1<<(7 - label%8)

#endif /* CODECOVERAGEARRAY_H_ */
