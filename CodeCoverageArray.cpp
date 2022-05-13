/*
 * CodeCoverageArray.h
 *
 *  Created on: 26 jan. 2022
 *      Author: llizhuoheng
 */

unsigned short  lastExecutedLabel = 0;
unsigned short  lastTransition[1518] = {0};              // Can be retrieved with 12 PQ9Bus frames
unsigned char   coverageArray[253] = {0};                // The largest size of PQ9Bus payload is 253 byte
