## SentinelCV
### Inspiration

Exploring the field of healthcare, we searched high and low for issues that weren't well noticed but nevertheless had huge implications on patients. Eventually, we came across the problem of pressure ulcers, or "Bedsores," which are an extremely common yet preventable complication that is rarely addressed by hospitals. Pressure ulcers occur when a patient lies in the same position for long periods of time, putting pressure on the joints and causing damage to tissue and skin. These can severely impact patient health and quality of life, and they affect approximately **2.5 million** patients each year, being the **second most common cause of lawsuits** ([source](https://www.ahrq.gov/patient-safety/settings/hospital/resource/pressureulcer/tool/pu1.html)). In addition to these, we found many more concerning statistics regarding pressure ulcers such as:

* Patients with pressure ulcers have significantly **higher mortality rates (9.1% vs 1.8%)** than those without ulcers ([Bauer et al., 2016](https://pubmed.ncbi.nlm.nih.gov/27861135/))
* Hospital-acquired pressure injuries in the United States alone are estimated to cost over **$26.8 billion**, which poses a significant financial burden on patients ([Padula and Delarmente, 2019](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7948545/))

Hearing these statistics, we immediately delved into a quest for possible solutions. While existing methods of addressing ulcers rely on manual intervention, we realized that leveraging existing hospital room cameras could provide a more efficient, cost-effective, and automated way to monitor patient movement. With this in mind, we set out to create _SentinelCV_, a system that uses computer vision to track patient activity, identifying risky periods of immobility and alerting caregivers in real-time.

### What We Learned

By developing _SentinelCV_, we gained a deeper understanding of the complexities of pressure ulcer formation and the critical role of frequent movements in their prevention. We developed our skills using computer vision techniques by implementing this technique to detect patients' positions during their sleep and determine the movements of specific key joints using regular RGB camera technology alone. 

In addition, we developed skills in integrating computer vision algorithms into a real-time monitoring system, unique in its ability to track multiple patients simultaneously. Building a user interface using Flask allowed us to implement complex vision processing techniques in a straightforward solution for healthcare professionals to deploy in a hospital environment. This project reinforced the importance of balancing technical innovation with practical usability in healthcare applications.

### Building the Project

_SentinelCV_ was built using a combination of computer vision, machine learning, and a Flask-based GUI. The core of our system relies on existing cameras in hospital rooms, eliminating the need for additional sensors or hardware. We started by developing an image processing pipeline using OpenCV and Google MediaPipe models to detect patients in bed and monitor their movements. We then proceeded to employ these models to identify subtle changes in body position and assess movement frequency, providing data to detect periods of risky immobility.

The captured video feeds are processed in real time by consolidating computer vision models with our own algorithms for patient detection. Specifically, our algorithm analyzes the patients' movement patterns, determining if they have remained in a constant position for too long based on medical guidelines for ulcer prevention. If a risky period of inactivity is detected, the system sends a notification through the GUI to alert medical staff, prompting them to take action.

The user interface was built with Flask to keep the system lightweight and simple. It displays the real-time monitoring status of each patient using JavaScript, including recent movement history and alert notifications. Nurses can access the interface from any device on the hospital network, allowing them to monitor multiple patients efficiently. By leveraging Flask, we ensured the system was easy to set up and use, requiring minimal staff training.

### Challenges We Faced

One of the primary challenges we encountered was achieving accurate patient detection and movement tracking using only the camera feeds. Unlike sensors, which can directly measure physical changes, cameras require complex image processing to interpret movements. We experimented with various computer vision models and techniques, including pose estimation algorithms, to enhance the accuracy of movement detection in different lighting conditions and room setups.

Another challenge was minimizing false alerts. As we developed our algorithms to categorize the patient's position and detect joint movements, one of the largest hurdles was fine-tuning the threshold levels. With even slight modifications to these levels, the accuracy rates of our models would vary drastically, with higher thresholds resulting in movements not being detected and low thresholds yielding false positive detections—both of which would decrease the efficacy of our solution. Through rigorous testing, however, we arrived at a set of thresholds that produced a high degree of accuracy as evidenced by our testing.

Building the real-time alert system using Flask also posed challenges. We had to ensure that the system could process video feeds and actively update the GUI with video, posture, and other data efficiently with minimal lag. Moreover, we had to ensure that our dynamic site could accommodate a variable number of patients. Through optimization of our server-side processing and careful management of data streams, however, we were able to ensure that hospital staff could receive timely and accurate data.

### What's Next?

In the future, we aim to incorporate more advanced machine learning algorithms to improve the accuracy of movement detection. This could include using convolutional neural networks (CNNs) for more precise pose estimation and even integrating predictive analytics to forecast potential pressure ulcer risks based on historical movement patterns. We also plan to add multi-room monitoring capabilities capable of combining video feeds from multiple cameras to handle larger hospital environments efficiently.

Additionally, we want to explore the integration of other hospital data sources, such as electronic health records (EHRs), to provide a more comprehensive patient risk assessment. In particular, we found that some patients may be at higher risk of developing ulcers than others. So, by integrating hospital data with our monitoring solution, we could automatically adjust individual patients’ movement analysis using their medical history and susceptibility to developing ulcers. This holistic approach could further empower caregivers to deliver proactive and personalized care. Accounting for this during the development phase of our project, we allowed for the assignment of individualized duration thresholds for patients in the backend.

### Conclusion

_SentinelCV_ leverages existing camera infrastructure in hospital rooms to provide a smart, proactive solution for preventing pressure ulcers. By using real-time computer vision monitoring, we greatly enhance patient safety throughout their stay at the hospital by addressing what the World Health Organization notes as one of the most common causes of patient harm in care facilities ([source](https://www.who.int/news-room/fact-sheets/detail/patient-safety)). In the process, we also ease hospital staff members’ busy schedules with timely alerts and work to reduce the lawsuits they may face from patients. Building this project taught us the value of combining technical expertise with practical healthcare solutions, resulting in an innovative system with a tangible real-world impact.
