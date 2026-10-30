package tickets;

import java.util.EnumSet;
import java.util.Objects;
import java.util.Set;

public class TicketTypeSeasonalRestricted extends TicketTypeSeasonal {

    private final Set<User.Occupation> occupations;

    public TicketTypeSeasonalRestricted(
            String name,
            double price,
            Set<Zone> zones,
            Season season,
            Set<User.Occupation> occupations) {
        super(name, price, zones, season);
        this.occupations = EnumSet.noneOf(User.Occupation.class);
        this.occupations.addAll(occupations);
    }

    @Override
    public boolean isValidFor(Trip trip, User user) {
        return occupations.contains(user.getOccupation())
            && super.isValidFor(trip, user);
    }

    @Override
    public boolean equals(Object other) {
        if (this == other) {
            return true;
        }
        if (other == null || getClass() != other.getClass()) {
            return false;
        }

        TicketTypeSeasonalRestricted ticket =
            (TicketTypeSeasonalRestricted) other;
        return super.equals(other)
            && occupations.equals(ticket.occupations);
    }

    @Override
    public int hashCode() {
        return Objects.hash(super.hashCode(), occupations);
    }
}