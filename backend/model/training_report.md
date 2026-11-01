# PhishGuard Training Report

Data file: `C:\Users\salla\Downloads\phiusiil+phishing+url+dataset (2)\PhiUSIIL_Phishing_URL_Dataset.csv`

## Limitation

This model uses only features that can be computed from the URL text. The original PhiUSIIL dataset also has features from page HTML and JavaScript. Those are NOT used here, so results are not comparable to the dataset's published results.

## Label mapping

Original PhiUSIIL: 0 = Phishing, 1 = Legitimate. PhishGuard: 0 = Legitimate, 1 = Phishing.

## Cleaning

- rows_loaded: 235795
- rows_dropped_missing: 0
- rows_dropped_bad_label: 0
- rows_dropped_invalid_url: 8
- rows_dropped_duplicates: 1569
- rows_clean: 234218
- clean_label_counts: {'phishing_1': 99369, 'legitimate_0': 134849}

## Split sizes (domain-grouped)

- train: 133462
- calibration: 55341
- test: 45415

## Test metrics (calibrated, untouched test split)

- Threshold: 0.5
- Accuracy: 0.9751
- Precision (phishing): 0.9871
- Recall (phishing): 0.9567
- F1 (phishing): 0.9717
- Macro F1: 0.9748
- Confusion matrix: TN=24931 FP=252 FN=877 TP=19355
- False positive rate: 0.0100
- False negative rate: 0.0433
- ROC-AUC: 0.9910
- PR-AUC: 0.9921
- Brier score: 0.0220

## Features

url_length, domain_length, is_ip_host, tld_length, num_subdomains, num_letters, letter_ratio, num_digits, digit_ratio, num_special, special_ratio, num_equals, num_question_marks, num_ampersands, num_percent_encoded, percent_encoded_ratio, num_hyphens_in_domain, num_dots, path_depth, is_https
