import { useToast } from './use-toast';
import NotificationCard from '../components/NotificationCard';

export const useNotification = () => {
  const { toast } = useToast();

  const showSecurityConfigurationComplete = ({
    completion = 0,
    recommendations = 0,
    dependentNodes = 0,
    vulnerabilities = null,
    smartNodeResult = null,
    autoVulnerabilityAnalysis = false
  }) => {
    // Determine notification type based on completion
    let type = 'success';
    if (completion < 50) {
      type = 'warning';
    } else if (completion < 100) {
      type = 'info';
    }

    // Create tip based on context
    let tip = null;
    if (!autoVulnerabilityAnalysis && completion >= 100) {
      tip = 'Use "Vulnerabilities" button to analyze security risks after completing all questions';
    } else if (completion < 100) {
      tip = 'Complete all security questions for comprehensive vulnerability analysis';
    }

    // Show main notification
    toast({
      title: "Security Configuration Completed!",
      description: (
        <NotificationCard
          title="Security Configuration Completed!"
          completion={completion}
          recommendations={recommendations}
          dependentNodes={dependentNodes}
          vulnerabilities={vulnerabilities}
          tip={tip}
          type={type}
        />
      ),
      duration: 5000,
    });

    // Show additional notification for smart node creation if present
    if (smartNodeResult && (smartNodeResult.nodesCreated > 0 || smartNodeResult.edgesCreated > 0)) {
      setTimeout(() => {
        toast({
          title: "Smart Links Created",
          description: (
            <NotificationCard
              title="Smart Links Created"
              type="info"
            />
          ),
          duration: 5000,
        });
      }, 500); // Slight delay to stack properly
    }
  };

  const showNodeCreation = (nodeType, count = 1) => {
    toast({
      title: `${nodeType} Node${count > 1 ? 's' : ''} Created`,
      description: (
        <NotificationCard
          title={`${nodeType} Node${count > 1 ? 's' : ''} Created`}
          type="success"
        />
      ),
      duration: 5000,
    });
  };

  const showError = (title, message) => {
    toast({
      title: title,
      description: (
        <NotificationCard
          title={title}
          tip={message}
          type="warning"
        />
      ),
      duration: 5000,
    });
  };

  const showInfo = (title, message, tip = null) => {
    toast({
      title: title,
      description: (
        <NotificationCard
          title={title}
          tip={tip || message}
          type="info"
        />
      ),
      duration: 5000,
    });
  };

  return {
    showSecurityConfigurationComplete,
    showNodeCreation,
    showError,
    showInfo
  };
};