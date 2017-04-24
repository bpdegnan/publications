filename = 'spisystem.csv';
M = csvread(filename,1,0);
title('System as a command decoder');
plot(M(:,1),M(:,2),M(:,1),M(:,4),M(:,1),M(:,6),M(:,1),M(:,8),M(:,1),M(:,10),M(:,1),M(:,12),M(:,1),M(:,14));

figure
title('System as a command decoder');
subplot(7,1,1);
plot(M(:,1),M(:,2));
xlabel('Time');
ylabel('Reset');
subplot(7,1,2);
plot(M(:,1),M(:,4),'r');
xlabel('Time');
ylabel('Clock');
subplot(7,1,3);
plot(M(:,1),M(:,6),'g');
xlabel('Time');
ylabel('Data');
subplot(7,1,4);
plot(M(:,1),M(:,8),'y');
xlabel('Time');
ylabel('Data Valid');
subplot(7,1,5);
plot(M(:,1),M(:,10),'b');
xlabel('Time');
ylabel('Driver Enable');
subplot(7,1,6);
plot(M(:,1),M(:,12),'r');
xlabel('Time');
ylabel('State 0');
subplot(7,1,7);
plot(M(:,1),M(:,14),'g');
xlabel('Time');
ylabel('State 1');

