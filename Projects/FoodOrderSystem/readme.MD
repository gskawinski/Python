
Food Orders is a Kafka-based event-driven food ordering system designed for scalability, leveraging Apache Kafka as a central event bus. It utilizes two Kafka topics: one for generating food orders from multiple restaurants concurrently, ensuring real-time processing capabilities, and another for handling order confirmations with email and data analytics. Once an order is received, the transaction unit performs validity checks before storing the raw data in MongoDB. A second real-time data stream is then generated, where the email confirmation unit sends timely confirmations to customers. The system also employs a client for real-time data analytics, extracting insights into customer preferences and business operations.

""" 
START KAFKA SERVER
- Start a single-node ZooKeeper instance using the following command:
sudo systemctl start zookeeper
- Verify the status of ZooKeeper:
sudo systemctl status zookeeper

Kafka requires ZooKeeper, so make sure ZooKeeper is running before starting Kafka.
- Now start the Kafka server:
sudo systemctl start kafka
- Check the status of the Kafka service:
sudo systemctl status kafka

"""

RUN in Order (in seperate terminal /process):
EmailConfirmation_Processor.py
DataAnalitics_Processor.py
Transaction_Processor.py
BackEnd_Processor.py
FrontEnd_Processor.py
